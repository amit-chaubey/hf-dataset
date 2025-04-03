#!/usr/bin/env python3
"""
Simple Book PDF to QA Dataset Generator

This script provides a structured, step-by-step approach to:
1. Extract text from a PDF book
2. Split text into meaningful sections
3. Generate question-answer pairs using LLM
4. Save results in CSV and Parquet formats
"""

import os
import re
import json
import time
import argparse
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PDF processing
import fitz  # PyMuPDF

# Data processing
import pandas as pd

# LLM integration
from openai import OpenAI

# Progress tracking
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# PDF TEXT EXTRACTION
# ------------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    logger.info(f"Extracting text from: {pdf_path}")
    start_time = time.time()
    
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        # Show progress for processing each page
        for page_num in tqdm(range(len(doc)), desc="Processing PDF pages"):
            page = doc[page_num]
            text += page.get_text() + "\n"
        
        doc.close()
        
        # Clean up the extracted text
        text = clean_text(text)
        
        duration = time.time() - start_time
        logger.info(f"Extracted {len(text)} characters in {duration:.2f} seconds")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise

def clean_text(text: str) -> str:
    """Clean the extracted text by removing noise."""
    # Remove header/footer page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common PDF artifacts
    text = text.replace('\x0c', '')  # Form feed character
    
    # Fix broken sentences
    text = re.sub(r'(\w)\n(\w)', r'\1 \2', text)
    
    # Replace multiple newlines with a single one
    text = re.sub(r'\n+', '\n', text)
    
    return text

# ------------------------------------------------------------------------------
# TEXT CHUNKING
# ------------------------------------------------------------------------------

def split_into_sections(text: str, min_section_length: int = 150, max_section_length: int = 1000) -> List[str]:
    """Split text into meaningful sections based on document structure."""
    logger.info("Splitting text into sections")
    start_time = time.time()
    
    # Force text into smaller chunks to ensure we get enough sections
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        # Fallback: split by newlines if no paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    # Always split into small chunks regardless of structure
    sections = []
    current_section = []
    current_length = 0
    
    for para in paragraphs:
        # If adding this paragraph would exceed max_section_length, save current chunk
        if current_length + len(para) > max_section_length and current_section:
            combined = "\n\n".join(current_section)
            if len(combined) >= min_section_length:
                sections.append(combined)
            current_section = []
            current_length = 0
        
        # If a single paragraph is too long, split it further by sentences
        if len(para) > max_section_length:
            sentence_chunks = split_by_sentences(para, min_section_length, max_section_length)
            for chunk in sentence_chunks:
                if len(chunk) >= min_section_length:
                    sections.append(chunk)
        else:
            current_section.append(para)
            current_length += len(para)
    
    # Add any remaining paragraphs
    if current_section:
        combined = "\n\n".join(current_section)
        if len(combined) >= min_section_length:
            sections.append(combined)
    
    # If we still don't have enough sections, force split large sections further
    if len(sections) < 100:  # Need at least 100 sections for 500+ QA pairs
        more_sections = []
        for section in sections:
            if len(section) > max_section_length / 2:  # More aggressive splitting
                smaller_chunks = split_by_sentences(section, min_section_length, max_section_length // 2)
                more_sections.extend(smaller_chunks)
            else:
                more_sections.append(section)
        sections = more_sections
    
    duration = time.time() - start_time
    logger.info(f"Split text into {len(sections)} sections in {duration:.2f} seconds")
    
    return sections

def split_large_section(section: str, min_length: int, max_length: int) -> List[str]:
    """Split a large section into smaller, meaningful subsections."""
    # Try to split by paragraphs first
    paragraphs = [p.strip() for p in section.split('\n\n') if p.strip()]
    
    if not paragraphs:
        # Fallback to sentence splitting if no paragraphs
        return split_by_sentences(section, min_length, max_length)
    
    subsections = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        if current_length + len(para) > max_length and current_chunk:
            # Save current chunk and start a new one
            subsections.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_length = len(para)
        else:
            current_chunk.append(para)
            current_length += len(para)
    
    # Add any remaining chunk
    if current_chunk:
        subsections.append('\n\n'.join(current_chunk))
    
    return subsections

def split_by_sentences(text: str, min_length: int, max_length: int) -> List[str]:
    """Split text by sentences to create chunks of appropriate size."""
    # Simple sentence detection
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) > max_length and current_chunk:
            # Save current chunk and start a new one
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence)
    
    # Add any remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# ------------------------------------------------------------------------------
# Clean up QA pairs function
# ------------------------------------------------------------------------------

def clean_qa_pairs(qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean up QA pairs by removing quotation marks and extra formatting."""
    cleaned_pairs = []
    
    for pair in qa_pairs:
        # Remove quotation marks from beginning and end of questions and answers
        question = pair["question"]
        answer = pair["answer"]
        
        # Clean question
        question = question.strip().strip('"\'').strip()
        # Remove any leading question numbers (e.g., "1. ")
        question = re.sub(r'^(\d+\.\s*)', '', question)
        
        # Clean answer
        answer = answer.strip().strip('"\'').strip()
        
        # Replace fancy quotes with regular quotes
        question = question.replace('"', '"').replace('"', '"')
        answer = answer.replace('"', '"').replace('"', '"')
        
        cleaned_pairs.append({
            "question": question,
            "answer": answer
        })
    
    return cleaned_pairs

# ------------------------------------------------------------------------------
# QUESTION-ANSWER GENERATION
# ------------------------------------------------------------------------------

def generate_qa_pairs(sections: List[str], max_pairs: int, 
                     model: str = "gpt-4-turbo", book_title: str = None) -> List[Dict[str, Any]]:
    """Generate question-answer pairs from text sections using an LLM."""
    logger.info(f"Generating up to {max_pairs} QA pairs using {model}")
    
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in your .env file.")
    
    client = OpenAI(api_key=api_key)
    qa_pairs = []
    
    # Create a context string for the prompt
    context = f" from {book_title}" if book_title else ""
    
    # Determine how many pairs to generate per section based on max_pairs and number of sections
    pairs_per_section = min(5, max(3, (max_pairs // len(sections)) + 1))
    logger.info(f"Generating approximately {pairs_per_section} QA pairs per section")
    
    # Process sections until we reach max_pairs
    progress_bar = tqdm(total=max_pairs, desc="Generating QA pairs")
    
    for section in sections:
        if len(qa_pairs) >= max_pairs:
            break
        
        # Format the prompt for this section
        prompt = f"""
        Generate {pairs_per_section} diverse question-answer pairs based on the following text{context}.
        
        Guidelines:
        - Create factual questions that can be directly answered from the text
        - Vary question types (who, what, when, where, why, how)
        - Ensure answers are concise and directly from the text
        - Focus on important information, not trivial details
        - Do NOT include quotation marks around questions or answers
        - Do NOT number questions (no "1.", "2.", etc.)
        
        Text:
        {section}
        
        Return only valid JSON with this exact structure:
        {{
            "qaPairs": [
                {{"question": "...", "answer": "..."}},
                {{"question": "...", "answer": "..."}}
                ... (repeat for all pairs)
            ]
        }}
        """
        
        try:
            # Make API call
            start_time = time.time()
            
            # Check if the model supports JSON response format
            json_format_models = ["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4-0125", "gpt-3.5-turbo-0125"]
            
            if any(m in model.lower() for m in json_format_models):
                # Use response_format for models that support it
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,  # Increased token limit for more pairs
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
            else:
                # For models that don't support response_format, rely on instruction in prompt
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,  # Increased token limit for more pairs
                    temperature=0.7
                )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            section_pairs = result.get("qaPairs", [])
            
            # Clean up the pairs
            section_pairs = clean_qa_pairs(section_pairs)
            
            # Add to collection
            for pair in section_pairs:
                if len(qa_pairs) < max_pairs:
                    qa_pairs.append({
                        "question": pair["question"],
                        "answer": pair["answer"]
                    })
                    progress_bar.update(1)
            
            # Show some debug info
            duration = time.time() - start_time
            logger.debug(f"Generated {len(section_pairs)} pairs in {duration:.2f}s")
            
            # Respect rate limits
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error generating QA pairs: {e}")
            time.sleep(2)  # Wait longer on error
    
    progress_bar.close()
    logger.info(f"Successfully generated {len(qa_pairs)} QA pairs")
    return qa_pairs

# ------------------------------------------------------------------------------
# SAVING AND EXPORTING
# ------------------------------------------------------------------------------

def save_dataset(qa_pairs: List[Dict[str, Any]], output_dir: str, 
                book_title: str = None) -> Dict[str, str]:
    """Save the dataset to CSV and Parquet formats."""
    logger.info(f"Saving dataset to: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as CSV
    csv_path = os.path.join(output_dir, "qa_dataset.csv")
    df = pd.DataFrame(qa_pairs)
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved {len(qa_pairs)} QA pairs to CSV: {csv_path}")
    
    # Save as Parquet
    parquet_path = os.path.join(output_dir, "qa_dataset.parquet")
    df.to_parquet(parquet_path, index=False)
    logger.info(f"Saved dataset to Parquet: {parquet_path}")
    
    # Create a readable preview file with truncated answers
    preview_path = os.path.join(output_dir, "qa_preview.csv")
    preview_df = df.copy()
    preview_df['answer'] = preview_df['answer'].apply(
        lambda x: x[:200] + "..." if len(x) > 200 else x
    )
    preview_df.to_csv(preview_path, index=False)
    logger.info(f"Created readable preview: {preview_path}")
    
    return {
        "csv": csv_path,
        "parquet": parquet_path,
        "preview": preview_path
    }

# ------------------------------------------------------------------------------
# MAIN WORKFLOW
# ------------------------------------------------------------------------------

def main():
    """Main workflow execution."""
    parser = argparse.ArgumentParser(description="Generate QA pairs from a book PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--book-title", default=None, help="Title of the book (optional)")
    parser.add_argument("--model", default="gpt-4-turbo", help="OpenAI model name")
    parser.add_argument("--max-pairs", type=int, default=100, help="Maximum number of QA pairs to generate")
    parser.add_argument("--min-section-length", type=int, default=150, 
                        help="Minimum length of text sections to process")
    parser.add_argument("--max-section-length", type=int, default=1000,
                        help="Maximum length of text sections before splitting")
    args = parser.parse_args()
    
    logger.info("Starting QA dataset generation process")
    start_time = time.time()
    
    # STEP 1: Extract text from PDF
    try:
        text = extract_text_from_pdf(args.pdf_path)
        logger.info(f"✓ STEP 1: Successfully extracted text from PDF ({len(text)} characters)")
    except Exception as e:
        logger.error(f"✗ STEP 1: Failed to extract text: {e}")
        return 1
    
    # STEP 2: Split text into sections
    try:
        # First try normal chunking
        sections = split_into_sections(text, args.min_section_length, args.max_section_length)
        
        # If we don't have enough sections for the requested number of pairs,
        # try more aggressive chunking
        min_sections_needed = max(100, args.max_pairs // 3)  # Need at least this many for max_pairs
        
        if len(sections) < min_sections_needed:
            logger.info(f"Need at least {min_sections_needed} sections for {args.max_pairs} pairs, using more aggressive chunking")
            # Try with smaller chunk size
            smaller_max_length = args.max_section_length // 2
            sections = split_into_sections(text, args.min_section_length, smaller_max_length)
            
            # If still not enough, use very aggressive sentence-based chunking
            if len(sections) < min_sections_needed:
                logger.info("Using very aggressive sentence-based chunking")
                # Split every section by sentences
                all_sentence_chunks = []
                for section in sections:
                    chunks = split_by_sentences(section, 100, 500)  # Very small chunks
                    all_sentence_chunks.extend(chunks)
                sections = all_sentence_chunks
        
        logger.info(f"✓ STEP 2: Successfully split text into {len(sections)} sections")
    except Exception as e:
        logger.error(f"✗ STEP 2: Failed to split text: {e}")
        return 1
    
    # STEP 3: Generate QA pairs
    try:
        qa_pairs = generate_qa_pairs(
            sections, 
            args.max_pairs,
            model=args.model,
            book_title=args.book_title
        )
        logger.info(f"✓ STEP 3: Successfully generated {len(qa_pairs)} QA pairs")
    except Exception as e:
        logger.error(f"✗ STEP 3: Failed to generate QA pairs: {e}")
        return 1
    
    # STEP 4: Save dataset
    try:
        file_paths = save_dataset(
            qa_pairs, 
            args.output_dir,
            book_title=args.book_title
        )
        logger.info(f"✓ STEP 4: Successfully saved dataset")
    except Exception as e:
        logger.error(f"✗ STEP 4: Failed to save dataset: {e}")
        return 1
    
    # Summary
    total_time = time.time() - start_time
    logger.info(f"Process completed in {total_time:.2f} seconds")
    logger.info(f"Generated {len(qa_pairs)} QA pairs")
    logger.info(f"CSV file: {file_paths['csv']}")
    logger.info(f"Parquet file: {file_paths['parquet']}")
    logger.info(f"Preview file: {file_paths['preview']}")
    
    return 0

if __name__ == "__main__":
    main() 
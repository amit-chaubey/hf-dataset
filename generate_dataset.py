import fitz  # PyMuPDF
import json
import os
import time
from tqdm import tqdm
import re
import argparse
import logging
from openai import OpenAI
from utils.env_loader import setup_env

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clean_text(text):
    """Clean the extracted text to remove unwanted characters"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers and headers
    text = re.sub(r'\n\d+\n', ' ', text)
    return text.strip()

def extract_text(pdf_path):
    """Extract text from PDF file and clean it"""
    logger.info(f"Extracting text from {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in tqdm(range(len(doc)), desc=f"Extracting pages from {os.path.basename(pdf_path)}"):
            text += doc[page].get_text()
        doc.close()
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def create_text_chunks(text, chunk_size=2000, overlap=200):
    """
    Split text into overlapping chunks for better context preservation
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length and end - start >= 100:  # Only add if chunk is meaningful
            # Find the last period to make better chunk boundaries
            last_period = text.rfind('. ', start, end)
            if last_period != -1 and last_period > start + chunk_size // 2:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position, with overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks

def generate_qa_pairs(client, text_chunk, model="gpt-3.5-turbo", num_pairs=5):
    """Generate Q&A pairs from a text chunk using OpenAI API"""
    prompt = f"""
    Generate {num_pairs} short, one-line Q&A pairs about Marxist theory from the following text.
    Each question should be factual and directly related to the content.
    Answers should be concise, accurate, and informative.
    
    Text:
    {text_chunk}
    
    Format each pair as:
    Q: [Question about something in the text]  
    A: [Concise, factual answer]
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip().split("\n")
    except Exception as e:
        logger.error(f"Error generating QA pairs: {e}")
        time.sleep(5)  # Back off in case of rate limiting
        return []

def parse_qa_pairs(qa_text):
    """Parse the generated Q&A text into structured pairs"""
    pairs = []
    current_q = None
    
    for line in qa_text:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("Q:"):
            current_q = line[2:].strip()
        elif line.startswith("A:") and current_q:
            answer = line[2:].strip()
            pairs.append((current_q, answer))
            current_q = None
    
    return pairs

def save_dataset(dataset, output_file):
    """Save the dataset to a JSONL file"""
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info(f"Dataset saved to {output_file}")

def main():
    # Load environment variables from .env file
    setup_env(required_vars=["OPENAI_API_KEY"])
    
    parser = argparse.ArgumentParser(description="Generate a Marx Q&A dataset from PDFs")
    parser.add_argument("--api_key", help="OpenAI API key")
    parser.add_argument("--model", default=os.getenv("MODEL", "gpt-3.5-turbo"), help="OpenAI model to use")
    parser.add_argument("--max_pairs", type=int, default=int(os.getenv("MAX_PAIRS", "1000")), help="Maximum number of Q&A pairs to generate")
    parser.add_argument("--output", default=os.getenv("OUTPUT_FILE", "marx_dataset.jsonl"), help="Output file name")
    parser.add_argument("--chunk_size", type=int, default=int(os.getenv("CHUNK_SIZE", "2000")), help="Size of text chunks for processing")
    args = parser.parse_args()
    
    # Get API key from args or environment variable
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or use --api_key")
        return
    
    client = OpenAI(api_key=api_key)
    
    # PDF files to process
    pdf_dir = "data"
    pdf_files = [
        os.path.join(pdf_dir, "Manifesto.pdf"),
        os.path.join(pdf_dir, "Capital-Volume-I.pdf")
    ]
    
    dataset = []
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            logger.warning(f"File {pdf_file} not found. Run download_pdfs.py first.")
            continue
            
        # Extract text from PDF
        text = extract_text(pdf_file)
        if not text:
            logger.warning(f"No text extracted from {pdf_file}. Skipping.")
            continue
            
        # Create text chunks
        chunks = create_text_chunks(text, chunk_size=args.chunk_size)
        logger.info(f"Created {len(chunks)} chunks from {pdf_file}")
        
        # Process each chunk
        for i, chunk in enumerate(tqdm(chunks, desc=f"Processing chunks from {os.path.basename(pdf_file)}")):
            # Generate QA pairs
            qa_text = generate_qa_pairs(client, chunk, model=args.model)
            
            # Parse and add to dataset
            qa_pairs = parse_qa_pairs(qa_text)
            for q, a in qa_pairs:
                dataset.append({
                    "conversation": [
                        {"from": "human", "value": q},
                        {"from": "assistant", "value": a}
                    ]
                })
            
            # Log progress
            logger.info(f"Generated {len(dataset)} pairs so far")
            
            # Check if we have enough data
            if len(dataset) >= args.max_pairs:
                logger.info(f"Reached target of {args.max_pairs} Q&A pairs")
                break
                
            # Rate limiting
            time.sleep(1)
        
        if len(dataset) >= args.max_pairs:
            break
    
    # Save dataset
    save_dataset(dataset[:args.max_pairs], args.output)
    logger.info(f"Successfully created dataset with {len(dataset[:args.max_pairs])} Q&A pairs")

if __name__ == "__main__":
    main() 
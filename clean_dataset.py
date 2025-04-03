#!/usr/bin/env python3
"""
Dataset Cleaner for QA Pairs

This script cleans the QA dataset by:
1. Removing duplicate questions
2. Removing quotation marks from questions and answers
3. Saving the clean dataset in CSV and Parquet formats
"""

import pandas as pd
import re
import os
import logging
import csv  # Added for CSV quoting constants

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text, is_answer=False):
    """Clean text by removing quotation marks and normalizing spaces.
    
    Args:
        text: The text to clean
        is_answer: Whether this is an answer (more aggressive cleaning)
    """
    if not isinstance(text, str):
        return text
    
    # First normalize the text by removing any leading/trailing spaces
    text = text.strip()
    
    # Replace fancy quotes with regular quotes first
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # If it's an answer, completely remove all types of quotes
    if is_answer:
        text = text.replace('"', '')
        text = text.replace("'", '')
        text = text.replace('`', '')
        # Remove any quote-like characters or symbols
        text = text.replace('"', '')
        text = text.replace('″', '')
        text = text.replace('″', '')
    else:
        # For questions, handle quoted phrases (like 'famed' or longer phrases)
        # Replace quotes around words or phrases with nothing
        text = re.sub(r"'([^']{1,50})'", r"\1", text)  # Handle up to 50 chars
        text = re.sub(r'"([^"]{1,50})"', r"\1", text)
        
        # Remove quotes at beginning and end
        if text.startswith('"') or text.startswith("'"):
            text = text[1:]
        if text.endswith('"') or text.endswith("'"):
            text = text[:-1]
            
        # Handle apostrophes in possessives - preserve them unless in quotes
        # No changes needed for possessives like "Pandavas'" since we're keeping those
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_dataset(input_file, output_dir='clean_output'):
    """
    Clean the dataset by removing duplicates and quotation marks.
    
    Args:
        input_file: Path to the input CSV file
        output_dir: Directory to save cleaned output files
    """
    logger.info(f"Reading dataset from {input_file}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the CSV file with proper quoting to handle existing quotes
    df = pd.read_csv(input_file, quoting=csv.QUOTE_MINIMAL)
    logger.info(f"Original dataset has {len(df)} QA pairs")
    
    # Clean questions and answers
    logger.info("Cleaning questions and answers")
    df['question'] = df['question'].apply(lambda x: clean_text(x, is_answer=False))
    df['answer'] = df['answer'].apply(lambda x: clean_text(x, is_answer=True))
    
    # Remove duplicate questions
    logger.info("Removing duplicate questions")
    df_no_dups = df.drop_duplicates(subset=['question'])
    logger.info(f"After removing duplicates: {len(df_no_dups)} QA pairs")
    
    # Save as CSV - use no quoting to avoid adding quotes
    csv_path = os.path.join(output_dir, "clean_qa_dataset.csv")
    df_no_dups.to_csv(csv_path, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
    logger.info(f"Saved clean dataset to CSV: {csv_path}")
    
    # Save as Parquet
    parquet_path = os.path.join(output_dir, "clean_qa_dataset.parquet")
    df_no_dups.to_parquet(parquet_path, index=False)
    logger.info(f"Saved clean dataset to Parquet: {parquet_path}")
    
    # Create a preview file with truncated answers
    preview_df = df_no_dups.copy()
    preview_df['answer'] = preview_df['answer'].apply(
        lambda x: x[:200] + "..." if isinstance(x, str) and len(x) > 200 else x
    )
    preview_path = os.path.join(output_dir, "clean_qa_preview.csv")
    preview_df.to_csv(preview_path, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
    logger.info(f"Created readable preview: {preview_path}")
    
    return {
        "csv": csv_path,
        "parquet": parquet_path,
        "preview": preview_path,
        "original_count": len(df),
        "cleaned_count": len(df_no_dups)
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean QA dataset by removing duplicates and quotation marks")
    parser.add_argument("--input", default="output/qa_dataset.csv", help="Input CSV file path")
    parser.add_argument("--output-dir", default="clean_output", help="Output directory")
    args = parser.parse_args()
    
    logger.info("Starting dataset cleaning process")
    result = clean_dataset(args.input, args.output_dir)
    
    logger.info(f"Cleaning complete:")
    logger.info(f"Original pairs: {result['original_count']}")
    logger.info(f"Cleaned pairs: {result['cleaned_count']}")
    logger.info(f"Removed {result['original_count'] - result['cleaned_count']} duplicate questions")
    logger.info(f"CSV file: {result['csv']}")
    logger.info(f"Parquet file: {result['parquet']}")
    logger.info(f"Preview file: {result['preview']}") 
#!/usr/bin/env python3
"""
NEET Topics Dataset Cleaner

This script cleans and restructures the NEET topics dataset for Hugging Face.
"""

import pandas as pd
import os

def clean_neet_dataset(input_file, output_dir='clean_neet_output'):
    """
    Clean and restructure the NEET topics dataset.
    
    Args:
        input_file: Path to the input CSV file
        output_dir: Directory to save cleaned output files
    """
    print(f"Reading dataset from {input_file}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    print(f"Original dataset has {len(df)} rows and {len(df.columns)} columns")
    
    # Display original columns
    print(f"\nOriginal columns: {list(df.columns)}")
    
    # Clean the dataset
    print("\nCleaning dataset...")
    
    # Remove unnecessary columns and keep essential ones
    essential_columns = ['Subject', 'Topic', 'SubTopic', 'Course', 'ExamType']
    df_clean = df[essential_columns].copy()
    
    # Remove rows with missing values in essential columns
    df_clean = df_clean.dropna(subset=['Subject', 'Topic', 'SubTopic'])
    
    # Remove duplicate rows
    df_clean = df_clean.drop_duplicates()
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    
    print(f"Cleaned dataset has {len(df_clean)} rows and {len(df_clean.columns)} columns")
    
    # Save cleaned dataset
    csv_path = os.path.join(output_dir, "neet_topics_clean.csv")
    df_clean.to_csv(csv_path, index=False)
    print(f"Saved cleaned dataset to CSV: {csv_path}")
    
    # Save as Parquet
    parquet_path = os.path.join(output_dir, "neet_topics_clean.parquet")
    df_clean.to_parquet(parquet_path, index=False)
    print(f"Saved cleaned dataset to Parquet: {parquet_path}")
    
    # Create a preview file
    preview_path = os.path.join(output_dir, "neet_topics_preview.csv")
    df_clean.head(100).to_csv(preview_path, index=False)
    print(f"Created preview file: {preview_path}")
    
    # Display sample of cleaned data
    print(f"\nSample of cleaned data:")
    print(df_clean.head(10))
    
    # Display unique subjects and topics
    print(f"\nUnique subjects: {df_clean['Subject'].unique()}")
    print(f"Total unique topics: {df_clean['Topic'].nunique()}")
    print(f"Total unique subtopics: {df_clean['SubTopic'].nunique()}")
    
    return {
        "csv": csv_path,
        "parquet": parquet_path,
        "preview": preview_path,
        "original_count": len(df),
        "cleaned_count": len(df_clean)
    }

if __name__ == "__main__":
    result = clean_neet_dataset("dataset/neet_topics.csv")
    
    print(f"\nCleaning complete:")
    print(f"Original rows: {result['original_count']}")
    print(f"Cleaned rows: {result['cleaned_count']}")
    print(f"Removed {result['original_count'] - result['cleaned_count']} rows")
    print(f"CSV file: {result['csv']}")
    print(f"Parquet file: {result['parquet']}")
    print(f"Preview file: {result['preview']}") 
#!/usr/bin/env python3
"""
Script to push the NEET topics dataset to Hugging Face Hub.
"""

import os
import sys
from datasets import Dataset
import pandas as pd
from huggingface_hub import login

def push_to_huggingface(input_path, repo_id, token=None):
    """
    Push a dataset to Hugging Face Hub.
    
    Args:
        input_path (str): Path to the input file (CSV or Parquet)
        repo_id (str): Hugging Face repository ID (e.g., 'username/dataset-name')
        token (str, optional): Hugging Face token. If None, will use stored credentials.
    """
    try:
        # Login to Hugging Face
        if token:
            login(token)
        else:
            print("No token provided. Using stored credentials if available.")
        
        print(f"Loading dataset from {input_path}...")
        
        # Load the data
        if input_path.endswith('.csv'):
            df = pd.read_csv(input_path)
        elif input_path.endswith('.parquet'):
            df = pd.read_parquet(input_path)
        else:
            raise ValueError("Input file must be CSV or Parquet")
        
        print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Convert to Hugging Face Dataset
        dataset = Dataset.from_pandas(df)
        print(f"Converted to Hugging Face Dataset format")
        
        # Push to Hub
        print(f"Pushing to {repo_id}...")
        dataset.push_to_hub(
            repo_id,
            token=token,
            private=False  # Set to True if you want it private
        )
        
        print(f"✅ Successfully pushed dataset to https://huggingface.co/datasets/{repo_id}")
        
    except Exception as e:
        print(f"❌ Error pushing dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Configuration
    input_file = "hf_upload_neet/neet_topics.parquet"  # Using Parquet for better performance
    repo_id = "sweatSmile/neet-topics"
    
    print(f"🚀 Pushing NEET Topics Dataset to Hugging Face...")
    print(f"Repository: {repo_id}")
    print(f"Input file: {input_file}")
    
    # Try without token first (using stored credentials)
    push_to_huggingface(input_file, repo_id) 
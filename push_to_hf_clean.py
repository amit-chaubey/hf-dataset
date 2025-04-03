#!/usr/bin/env python3
"""
Push Cleaned QA Dataset to Hugging Face

This script pushes the cleaned QA dataset to Hugging Face Datasets.
"""

import os
import argparse
import pandas as pd
from huggingface_hub import HfApi, login
from datasets import Dataset

def push_to_huggingface(input_path, repo_id, token=None):
    """
    Push the cleaned dataset to Hugging Face.
    
    Args:
        input_path: Path to the cleaned Parquet file
        repo_id: Hugging Face repository ID (username/repo-name)
        token: Hugging Face token
    """
    # Login to Hugging Face
    if token:
        login(token)
    else:
        print("No token provided. Using stored credentials if available.")
    
    # Load the dataset
    print(f"Loading dataset from {input_path}")
    df = pd.read_parquet(input_path)
    
    # Convert to Hugging Face Dataset
    dataset = Dataset.from_pandas(df)
    
    # Push to Hugging Face
    print(f"Pushing dataset to Hugging Face: {repo_id}")
    dataset.push_to_hub(
        repo_id,
        private=False,
        token=token
    )
    
    print(f"Successfully pushed dataset to {repo_id}")
    print(f"View your dataset at: https://huggingface.co/datasets/{repo_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push cleaned QA dataset to Hugging Face")
    parser.add_argument("--input", default="clean_output/clean_qa_dataset.parquet", 
                        help="Path to the cleaned Parquet file")
    parser.add_argument("--repo-id", required=True, 
                        help="Hugging Face repository ID (username/repo-name)")
    parser.add_argument("--token", default=None, 
                        help="Hugging Face token (if not provided, will use stored credentials)")
    
    args = parser.parse_args()
    
    push_to_huggingface(args.input, args.repo_id, args.token) 
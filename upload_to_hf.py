import os
import json
import argparse
from datasets import Dataset
from huggingface_hub import login, HfApi
import pandas as pd
from utils.env_loader import setup_env

def load_jsonl(file_path):
    """Load a JSONL file into a list of dictionaries"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def main():
    # Load environment variables from .env file
    setup_env(required_vars=["HF_TOKEN"])
    
    parser = argparse.ArgumentParser(description="Upload dataset to Hugging Face Hub")
    parser.add_argument("--input", default=os.getenv("OUTPUT_FILE", "marx_dataset.jsonl"), help="Input JSONL file path")
    parser.add_argument("--input_dir", default=os.getenv("OUTPUT_DIR"), help="Directory containing all dataset formats (JSONL, CSV, Parquet)")
    parser.add_argument("--repo_id", required=True, help="Hugging Face repository ID (e.g., username/dataset-name)")
    parser.add_argument("--token", help="Hugging Face API token")
    args = parser.parse_args()
    
    # Get token from args or environment variable
    token = args.token or os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("No Hugging Face token provided. Set HF_TOKEN environment variable or use --token")
    
    # Login to Hugging Face
    login(token=token)
    
    # Load the dataset
    if args.input_dir and os.path.exists(args.input_dir):
        # Using multiple format files from a directory
        input_path = args.input_dir
        jsonl_file = os.path.join(input_path, os.path.basename(args.input))
        
        if not os.path.exists(jsonl_file):
            # Look for any JSONL file
            jsonl_files = [f for f in os.listdir(input_path) if f.endswith('.jsonl')]
            if jsonl_files:
                jsonl_file = os.path.join(input_path, jsonl_files[0])
            else:
                raise ValueError(f"No JSONL file found in {input_path}")
        
        print(f"Loading dataset from {jsonl_file}...")
        data = load_jsonl(jsonl_file)
        print(f"Loaded {len(data)} conversation pairs")
        
        # Get base name for other formats
        base_name = os.path.splitext(os.path.basename(jsonl_file))[0]
        csv_file = os.path.join(input_path, f"{base_name}.csv")
        parquet_file = os.path.join(input_path, f"{base_name}.parquet")
        
        # Check which formats exist
        formats = {"jsonl": os.path.exists(jsonl_file)}
        formats["csv"] = os.path.exists(csv_file)
        formats["parquet"] = os.path.exists(parquet_file)
        
        print(f"Found dataset in formats: {', '.join([fmt for fmt, exists in formats.items() if exists])}")
    else:
        # Using single JSONL file
        if not os.path.exists(args.input):
            raise ValueError(f"Input file {args.input} not found")
            
        print(f"Loading dataset from {args.input}...")
        data = load_jsonl(args.input)
        print(f"Loaded {len(data)} conversation pairs")
        formats = {"jsonl": True, "csv": False, "parquet": False}
    
    # Convert to Hugging Face Dataset
    dataset = Dataset.from_list(data)
    
    # Create repository description
    dataset_info = f"""# Marx Conversational Dataset

A dataset of {len(data)} conversational Q&A pairs generated from Marxist theory texts including:
- The Communist Manifesto
- Das Kapital Volume 1

Each entry contains a human question and an assistant answer about Marxist theory concepts.

## Dataset Format

The dataset is available in the following formats:
- JSONL (primary format with nested conversation structure)
- CSV (flattened with 'question' and 'answer' columns)
- Parquet (Apache Parquet format)

### JSONL Format Example:
```json
{{
  "conversation": [
    {{"from": "human", "value": "What is capitalism?"}},
    {{"from": "assistant", "value": "Capitalism is an economic system based on private ownership and profit-driven production."}}
  ]
}}
```

## Usage

This dataset is designed for fine-tuning conversational AI models to respond to questions about Marxist theory.
"""

    # Push to Hugging Face Hub
    print(f"Uploading dataset to {args.repo_id}...")
    dataset.push_to_hub(
        args.repo_id,
        token=token,
        commit_message="Upload Marx conversational dataset",
        embed_external_files=False
    )
    
    # Update README
    api = HfApi()
    api.upload_file(
        path_or_fileobj=dataset_info.encode(),
        path_in_repo="README.md",
        repo_id=args.repo_id,
        token=token,
        commit_message="Update README"
    )
    
    # Upload additional format files if they exist
    if args.input_dir:
        if formats["csv"]:
            print(f"Uploading CSV format...")
            api.upload_file(
                path_or_fileobj=csv_file,
                path_in_repo=os.path.basename(csv_file),
                repo_id=args.repo_id,
                token=token,
                commit_message="Add CSV format"
            )
        
        if formats["parquet"]:
            print(f"Uploading Parquet format...")
            api.upload_file(
                path_or_fileobj=parquet_file,
                path_in_repo=os.path.basename(parquet_file),
                repo_id=args.repo_id,
                token=token,
                commit_message="Add Parquet format"
            )
    
    print(f"Dataset successfully uploaded to https://huggingface.co/datasets/{args.repo_id}")
    print(f"Available formats: {', '.join([fmt for fmt, exists in formats.items() if exists])}")

if __name__ == "__main__":
    main() 
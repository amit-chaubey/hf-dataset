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
    
    parser = argparse.ArgumentParser(description="Upload fixed format dataset to Hugging Face Hub")
    parser.add_argument("--input_dir", default="dataset_hf", help="Directory containing the fixed format files")
    parser.add_argument("--base_name", default="marx_dataset", help="Base name of the dataset files")
    parser.add_argument("--repo_id", required=True, help="Hugging Face repository ID (e.g., username/dataset-name)")
    parser.add_argument("--token", help="Hugging Face API token")
    args = parser.parse_args()
    
    # Get token from args or environment variable
    token = args.token or os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("No Hugging Face token provided. Set HF_TOKEN environment variable or use --token")
    
    # Login to Hugging Face
    login(token=token)
    
    # Prepare file paths
    jsonl_file = os.path.join(args.input_dir, f"{args.base_name}.jsonl")
    csv_file = os.path.join(args.input_dir, f"{args.base_name}.csv")
    parquet_file = os.path.join(args.input_dir, f"{args.base_name}.parquet")
    
    # Check which formats exist
    formats = {
        "jsonl": os.path.exists(jsonl_file),
        "csv": os.path.exists(csv_file),
        "parquet": os.path.exists(parquet_file)
    }
    
    # Load the primary JSONL dataset
    if not formats["jsonl"]:
        raise ValueError(f"JSONL file not found: {jsonl_file}")
    
    print(f"Loading dataset from {jsonl_file}...")
    conversations = load_jsonl(jsonl_file)
    print(f"Loaded {len(conversations)} conversation pairs")
    
    # Create a Hugging Face dataset
    # For this format, we create a dataset with a 'conversations' field
    hf_data = [{"conversations": conv} for conv in conversations]
    dataset = Dataset.from_list(hf_data)
    
    # Create repository description
    dataset_info = f"""# Marx Conversational Dataset

A dataset of {len(conversations)} conversational Q&A pairs generated from Marxist theory texts including:
- The Communist Manifesto
- Das Kapital Volume 1

Each entry contains a human question and a gpt response about Marxist theory concepts.

## Dataset Format

The dataset follows the conversational format with a list of messages, each with 'from' and 'value' fields:

```json
[
  {{"from": "human", "value": "What is capitalism?"}},
  {{"from": "gpt", "value": "Capitalism is an economic system based on private ownership and profit-driven production."}}
]
```

The dataset is available in the following formats:
- JSONL (primary format with conversational structure)
- CSV (flattened with 'question' and 'answer' columns)
- Parquet (Apache Parquet format)

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
    
    # Upload additional format files
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
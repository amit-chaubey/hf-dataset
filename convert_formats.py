import json
import pandas as pd
import os
import argparse
from tqdm import tqdm
from utils.env_loader import setup_env

def load_jsonl(file_path):
    """Load a JSONL file into a list of dictionaries"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def convert_to_csv(data, output_file):
    """Convert dataset to CSV format"""
    # Extract questions and answers into a flat structure
    rows = []
    for item in data:
        if "conversation" in item and len(item["conversation"]) >= 2:
            question = item["conversation"][0].get("value", "")
            answer = item["conversation"][1].get("value", "")
            rows.append({
                "question": question,
                "answer": answer
            })
    
    # Create a DataFrame and save as CSV
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, encoding='utf-8')
    return len(rows)

def convert_to_parquet(data, output_file):
    """Convert dataset to Parquet format"""
    # Extract data in a similar structure to the original
    # This maintains the nested structure which Parquet can handle
    df = pd.DataFrame(data)
    df.to_parquet(output_file, index=False)
    return len(data)

def main():
    # Load environment variables from .env file
    setup_env()
    
    parser = argparse.ArgumentParser(description="Convert dataset to multiple formats")
    parser.add_argument("--input", default=os.getenv("OUTPUT_FILE", "marx_dataset.jsonl"), help="Input JSONL file path")
    parser.add_argument("--output_dir", default=os.getenv("OUTPUT_DIR", "dataset"), help="Output directory for converted files")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set output file paths
    jsonl_output = os.path.join(args.output_dir, os.path.basename(args.input))
    csv_output = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input))[0] + ".csv")
    parquet_output = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input))[0] + ".parquet")
    
    # Load the JSONL data
    print(f"Loading dataset from {args.input}...")
    data = load_jsonl(args.input)
    print(f"Loaded {len(data)} conversation pairs")
    
    # Copy the original JSONL to the output directory
    with open(jsonl_output, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Copied JSONL dataset to {jsonl_output}")
    
    # Convert to CSV
    print(f"Converting to CSV format...")
    csv_count = convert_to_csv(data, csv_output)
    print(f"Converted {csv_count} pairs to CSV format: {csv_output}")
    
    # Convert to Parquet
    print(f"Converting to Parquet format...")
    parquet_count = convert_to_parquet(data, parquet_output)
    print(f"Converted {parquet_count} pairs to Parquet format: {parquet_output}")
    
    print("\nConversion complete! The dataset is now available in the following formats:")
    print(f"- JSONL: {jsonl_output}")
    print(f"- CSV: {csv_output}")
    print(f"- Parquet: {parquet_output}")
    print("\nYou can now push these files to Hugging Face.")

if __name__ == "__main__":
    main()
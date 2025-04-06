import json
import os
import argparse
from tqdm import tqdm

def fix_jsonl_format(input_file, output_file):
    """
    Fix JSONL format to match the Hugging Face expected format:
    From:
    {"conversation": [{"from": "human", "value": "..."}, {"from": "assistant", "value": "..."}]}
    
    To:
    [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]
    """
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line.strip())
            if "conversation" in item and len(item["conversation"]) >= 2:
                # Rename "assistant" to "gpt" to match Hugging Face format
                conversation = item["conversation"]
                for message in conversation:
                    if message["from"] == "assistant":
                        message["from"] = "gpt"
                data.append(conversation)
    
    # Save in the corrected format
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    return len(data)

def fix_csv_format(input_file, output_file):
    """
    For CSV, we keep it as is but rename headers if needed
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    # Just copy the file but ensure consistent quoting if needed
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in lines:
            outfile.write(line)
    
    return len(lines) - 1  # Subtract header line

def main():
    parser = argparse.ArgumentParser(description="Fix Hugging Face dataset format")
    parser.add_argument("--input_dir", default="dataset", help="Input directory containing the dataset files")
    parser.add_argument("--output_dir", default="dataset_hf", help="Output directory for fixed format files")
    parser.add_argument("--base_name", default="marx_dataset", help="Base name of the dataset files")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Fix JSONL format
    jsonl_input = os.path.join(args.input_dir, f"{args.base_name}.jsonl")
    jsonl_output = os.path.join(args.output_dir, f"{args.base_name}.jsonl")
    
    if os.path.exists(jsonl_input):
        print(f"Fixing JSONL format: {jsonl_input} -> {jsonl_output}")
        count = fix_jsonl_format(jsonl_input, jsonl_output)
        print(f"Processed {count} conversation pairs")
    else:
        print(f"JSONL file not found: {jsonl_input}")
    
    # Copy CSV file
    csv_input = os.path.join(args.input_dir, f"{args.base_name}.csv")
    csv_output = os.path.join(args.output_dir, f"{args.base_name}.csv")
    
    if os.path.exists(csv_input):
        print(f"Copying CSV file: {csv_input} -> {csv_output}")
        count = fix_csv_format(csv_input, csv_output)
        print(f"Processed {count} rows")
    else:
        print(f"CSV file not found: {csv_input}")
    
    # Copy Parquet file
    parquet_input = os.path.join(args.input_dir, f"{args.base_name}.parquet")
    parquet_output = os.path.join(args.output_dir, f"{args.base_name}.parquet")
    
    if os.path.exists(parquet_input):
        print(f"Copying Parquet file: {parquet_input} -> {parquet_output}")
        import shutil
        shutil.copy2(parquet_input, parquet_output)
        print(f"Copied Parquet file")
    else:
        print(f"Parquet file not found: {parquet_input}")
    
    print(f"\nFormat fixing complete. Files available in: {args.output_dir}")

if __name__ == "__main__":
    main() 
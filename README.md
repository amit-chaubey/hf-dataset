# Marx Conversational Dataset Creator

Tools for creating, formatting, and uploading a conversational dataset based on Marxist theory texts.

## Overview

This repository contains code to generate a Q&A dataset from "The Communist Manifesto" and "Das Kapital" using OpenAI's API. The resulting dataset can be used for fine-tuning conversational AI models to respond to questions about Marxist theory.

🔗 **Dataset available on Hugging Face**: [sweatSmile/marx-dataset](https://huggingface.co/datasets/sweatSmile/marx-dataset)

## Key Features

- Downloads source PDFs automatically
- Extracts text and generates Q&A pairs using OpenAI API
- Converts the dataset to multiple formats (JSONL, CSV, Parquet)
- Properly formats data for Hugging Face compatibility
- Uploads the dataset to Hugging Face

## Repository Structure

```
marxist-dataset-creator/
├── download_pdfs.py          # Downloads source PDFs
├── generate_dataset.py       # Generates Q&A pairs from PDFs
├── convert_formats.py        # Converts dataset to multiple formats
├── fix_format.py             # Fixes format for Hugging Face compatibility
├── upload_to_hf.py           # Uploads dataset to Hugging Face
├── upload_hf_fixed.py        # Uploads fixed format dataset
├── run_pipeline.sh           # Script to run the entire pipeline
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment file
├── .env.sample               # Sample environment file with comments
└── utils/                    # Utility modules
    ├── __init__.py
    └── env_loader.py         # Environment variable loader
```

## Prerequisites

- Python 3.8+
- OpenAI API key
- Hugging Face account and API token (for uploading)

## Setup

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env file with your API keys
```

## Usage

### Full Pipeline

Run the entire dataset generation process in one command:

```bash
./run_pipeline.sh --repo_id your-username/dataset-name
```

Options:
- `--api_key` - OpenAI API key (or set via environment)
- `--hf_token` - Hugging Face token (or set via environment)
- `--max_pairs` - Number of pairs to generate (default: 1000)
- `--skip_upload` - Skip uploading to Hugging Face
- `--skip_conversion` - Skip format conversion
- Full list of options: `./run_pipeline.sh --help`

### Individual Steps

You can also run each step individually:

1. **Download PDFs**:
```bash
python download_pdfs.py
```

2. **Generate Dataset**:
```bash
python generate_dataset.py
```

3. **Convert Formats**:
```bash
python convert_formats.py
```

4. **Fix Format for Hugging Face**:
```bash
python fix_format.py
```

5. **Upload to Hugging Face**:
```bash
python upload_hf_fixed.py --repo_id your-username/dataset-name
```

## Environment Variables

Set these in your `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
HF_TOKEN=your_huggingface_token
MODEL=gpt-3.5-turbo
MAX_PAIRS=1000
OUTPUT_FILE=marx_dataset.jsonl
OUTPUT_DIR=dataset
```

## Dataset Format

The dataset follows the conversational format with a list of messages:

```json
[
  {"from": "human", "value": "What is capitalism?"},
  {"from": "gpt", "value": "Capitalism is an economic system based on private ownership and profit-driven production."}
]
```

## License

This project is for educational purposes. Please ensure you comply with OpenAI's terms of service and the licensing of the original texts. 
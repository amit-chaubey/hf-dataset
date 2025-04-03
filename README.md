# Book PDF to Q&A Dataset Generator

This tool processes book PDFs to generate question-answer pairs using LLMs (OpenAI or DeepSeek) and prepares datasets in CSV and Parquet formats for Hugging Face.

## Features

- Extract and process text from PDF books
- Split text into manageable chunks with intelligent boundaries
- Generate high-quality question-answer pairs using OpenAI (GPT-4) or DeepSeek LLMs
- Export datasets to CSV and Parquet formats for Hugging Face
- Configurable parameters for customization

## Setup

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```
3. Place your PDF book files in the `dataset` folder
4. Set up your API keys:
   - Copy `.env.template` to `.env`
   - Add your API keys to the `.env` file:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```
   - The `.env` file is in `.gitignore` so your API keys won't be exposed if you push your code

## Usage

### Basic Usage

```bash
python qa_generator.py dataset/your-book.pdf
```

This will process the PDF and generate up to 1000 question-answer pairs using OpenAI's GPT-4 model. Results will be saved to the `output` directory.

### Advanced Options

```bash
python qa_generator.py dataset/your-book.pdf \
  --output-dir custom_output \
  --llm-provider deepseek \
  --model deepseek-chat \
  --api-key your_api_key \
  --chunk-size 1500 \
  --chunk-overlap 300 \
  --max-rows 500
```

### Command-line Arguments

- `pdf_path`: Path to the PDF file (required)
- `--output-dir`: Directory to store output files (default: "output")
- `--llm-provider`: LLM provider - "openai" or "deepseek" (default: "openai")
- `--model`: Model name (default: "gpt-4")
- `--api-key`: API key (uses environment variable if not provided)
- `--chunk-size`: Chunk size in characters (default: 1000)
- `--chunk-overlap`: Chunk overlap in characters (default: 200)
- `--max-rows`: Maximum number of QA pairs to generate (default: 1000)

## Environment Variables

API keys can be specified in the `.env` file (preferred) or as environment variables. The script uses these environment variables:

- `OPENAI_API_KEY`: For OpenAI API access
- `DEEPSEEK_API_KEY`: For DeepSeek API access
- `HF_TOKEN`: For Hugging Face authentication

If using environment variables directly:
```bash
export OPENAI_API_KEY="your-api-key-here"
python qa_generator.py dataset/your-book.pdf
```

## Output

The script generates two output files:
- `qa_dataset.csv`: CSV file with question-answer pairs
- `qa_dataset.parquet`: Parquet format file for Hugging Face datasets

## Pushing to Hugging Face

After generating your dataset, you can upload it to the Hugging Face Hub using the Hugging Face CLI:

```bash
# Install the Hugging Face Hub CLI
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login

# Upload your dataset (replace placeholders with your information)
huggingface-cli upload-dataset \
  --path output/qa_dataset.parquet \
  --name your-username/dataset-name \
  --type dataset
```

## License

MIT 
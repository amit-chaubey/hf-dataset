# Bhagavad Gita QA Dataset

## Description
This dataset contains 500 question-answer pairs based on Edwin Arnold's translation of the Bhagavad Gita. The questions cover various aspects of the text, including philosophical concepts, characters, events, and teachings from the ancient Indian scripture.

## Structure
The dataset is provided in two formats:
- CSV format: `bhagavad_gita_qa.csv`
- Parquet format: `bhagavad_gita_qa.parquet`

Each record contains two fields:
- `question`: A question about the Bhagavad Gita
- `answer`: The corresponding answer from the text

## Content
The dataset covers the entire Bhagavad Gita, including all 18 chapters. Questions are varied in style and complexity, providing a comprehensive coverage of the text's content.

## Source
The questions and answers were generated based on Edwin Arnold's translation of the Bhagavad Gita, originally published circa 300 B.C. The text was processed to extract meaningful sections, and question-answer pairs were generated using LLM technology.

## Usage
This dataset can be used for:
- Fine-tuning question-answering models
- Religious and philosophical text understanding
- Educational tools for studying the Bhagavad Gita
- Testing retrieval-based QA systems

## Examples

1. **Question**: Who is the translator of the Bhagavad Gita edition mentioned?  
   **Answer**: Edwin Arnold

2. **Question**: What is the title of Chapter 1 in the Bhagavad Gita?  
   **Answer**: Of the Distress of Arjuna

3. **Question**: What was Arjuna's state when he saw his kinsmen arrayed for battle?  
   **Answer**: He was overcome with grief and dejection

## License
This dataset is made available for research and educational purposes.

## Citation
If you use this dataset, please cite:
```
@dataset{bhagavad_gita_qa_2025,
  author    = {sweatSmile},
  title     = {Bhagavad Gita Question-Answer Dataset},
  year      = {2025},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/sweatSmile/Bhagavad-Gita-Vyasa-Edwin-Arnold}
}
``` 
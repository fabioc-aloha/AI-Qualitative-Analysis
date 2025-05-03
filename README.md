# MCEM-Interview-Processing

An automated tool for processing and analyzing customer interview transcripts using Azure OpenAI, aligning discussions with Microsoft's Customer Engagement Model (MCEM) framework.

## Features

- Processes interview transcripts using Azure OpenAI's GPT-4 model
- Generates structured analysis reports in both Markdown and Word formats
- Handles large transcripts through intelligent chunking
- Applies MCEM framework to organize insights and recommendations
- Preserves direct customer quotes and specific metrics
- Generates comprehensive analysis including:
  - Company background and context
  - Executive summary
  - Stage-by-stage MCEM analysis
  - Strategic recommendations
  - Detailed feedback analysis

## Prerequisites

- Python 3.x
- Azure OpenAI API access
- Pandoc (for Word document conversion)
- Required Python packages:
  - openai
  - python-dotenv
  - tiktoken

## Setup

1. Clone this repository
2. Create a `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_DEPLOYMENT=your_deployment
   AZURE_OPENAI_API_VERSION=your_api_version
   ```
3. Install required packages:
   ```bash
   pip install openai python-dotenv tiktoken
   ```

## Usage

1. Place interview transcripts in the `transcripts/` directory as .txt files
2. Run the script:
   ```bash
   python process_transcripts.py
   ```
3. Find generated analyses in the `reports/` directory in both .md and .docx formats

## Project Structure

```
├── process_transcripts.py    # Main processing script
├── AnalysisTemplate.txt     # Template for analysis reports
├── .env                     # Configuration file (not in repo)
├── transcripts/            # Input directory for transcripts
└── reports/               # Output directory for analyses
```

## Analysis Output

The generated analysis includes:
- Executive Summary
- Company Background
- Interview Details
- MCEM Stage Analysis
- Strategic Recommendations
- Additional Customer Feedback
- Comprehensive Summary Table

## Note

Ensure sensitive information is properly handled. The `.env` file and customer transcripts are excluded from version control by default.

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
  - Role-based insights and action items
  - Sentiment analysis and mood indicators
  - Key metrics and success indicators

## Prerequisites

- Python 3.x
- Azure OpenAI API access
- Pandoc (for Word document conversion)
- Required Python packages (see requirements.txt)

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
   pip install -r requirements.txt
   ```

## Usage

1. Place interview transcripts in the `transcripts/` directory as .txt files
2. Run the script:
   ```bash
   python process_transcripts.py
   ```
3. Find generated analyses in the `reports/` directory in both .md and .docx formats

## Configuration File Support

This project now supports advanced configuration via a YAML file (`config.yaml`).

- All major settings (Azure credentials, chunk size, output formats, template selection, etc.) can be managed in `config.yaml`.
- Environment variables in the config (e.g., `${AZURE_OPENAI_API_KEY}`) are automatically expanded.
- The main script loads and applies these settings at runtime.
- See the provided `config.yaml` for an example and available options.

### Example `config.yaml`

```yaml
azure:
  api_key: "${AZURE_OPENAI_API_KEY}"
  api_version: "${AZURE_OPENAI_API_VERSION}"
  endpoint: "${AZURE_OPENAI_ENDPOINT}"
  deployment: "${AZURE_OPENAI_DEPLOYMENT}"
processing:
  chunk_size: 80000
  max_completion_tokens: 16000
  language_detection: false
  output_format: ["md", "docx"]
  template_path: "AnalysisTemplate.txt"
  summary_report: true
  dry_run: false
  log_to_file: false
  log_file_path: "logs/processing.log"
  analysis_template: "default"
  available_templates:
    default: "AnalysisTemplate.txt"
```

## Project Structure

```
├── process_transcripts.py    # Main processing script
├── AnalysisTemplate.txt     # Template for analysis reports
├── requirements.txt         # Python package requirements
├── .env                     # Configuration file (not in repo)
├── transcripts/            # Input directory for transcripts
└── reports/               # Output directory for analyses
```

## Analysis Output

The generated analysis includes:
- Executive Summary
- Company Background
- Interview Details
- MCEM Stage Analysis (Listen & Consult through Manage & Optimize)
- Strategic Recommendations
- Additional Customer Feedback
- Role-based Summary Table with Action Items
- Sentiment Analysis and Key Metrics

## Best Practices

- Keep transcripts in plain text format (.txt)
- One transcript per interview session
- Use consistent naming conventions for transcript files
- Review generated reports for sensitive information before sharing
- Regular backups of analysis outputs recommended

## Note

- The `.env` file and customer transcripts are excluded from version control by default
- Ensure compliance with data privacy requirements when handling customer information
- Regular updates to the Azure OpenAI API may require configuration adjustments

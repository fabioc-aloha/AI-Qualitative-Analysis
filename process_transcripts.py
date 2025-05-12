"""
MCEM Interview Processing Script

This script processes customer interview transcripts using Azure OpenAI's GPT-4 model to generate
structured analysis reports based on Microsoft's Customer Engagement Model (MCEM) framework.
It handles both small and large transcripts through intelligent chunking and generates output
in both Markdown and Word document formats.

Requirements:
    - Python 3.x
    - Azure OpenAI API access
    - Environment variables set in .env file:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_API_VERSION
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_DEPLOYMENT
    - Pandoc installed for Word document conversion
    - Required packages: openai, python-dotenv, tiktoken

Usage:
    1. Place interview transcripts in the 'transcripts/' directory as .txt files
    2. Ensure AnalysisTemplate.txt exists with the desired template
    3. Run the script: python process_transcripts.py
    4. Generated analyses will be in the 'reports/' directory
"""

from dotenv import load_dotenv
from utils.env_utils import setup_logging, check_env_vars, check_pandoc_installed
from utils.file_utils import get_client, ensure_reports_dir, load_analysis_template
from processing.batch_processing import process_all_transcripts
from utils.config_utils import load_config

# --- Main Entry Point ---
def main():
    """
    Main execution function that:
    1. Sets up logging
    2. Loads environment variables from .env
    3. Loads configuration from config.yaml
    4. Validates environment and dependencies
    5. Initializes Azure OpenAI client
    6. Creates output directory if needed
    7. Processes all .txt files in the transcripts directory
    8. Generates both markdown and Word document outputs
    """
    setup_logging()
    load_dotenv()  # Load .env first so env vars are available for config expansion
    config = load_config()
    check_env_vars([
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT"
    ])
    check_pandoc_installed()
    client = get_client()
    reports_dir = ensure_reports_dir()
    template_path = config['processing'].get('template_path', 'AnalysisTemplate-Improved.txt')
    template = load_analysis_template(template_path)
    process_all_transcripts(client, template, reports_dir)

if __name__ == "__main__":
    main()
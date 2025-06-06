"""
MCEM Interview Processing Script

This script processes customer interview transcripts using Azure OpenAI's GPT-4 model to generate
structured analysis reports based on Microsoft's Customer Engagement Model (MCEM) framework.
It handles both small and large transcripts through intelligent chunking and generates output
in both Markdown and Word document formats.

Additionally, the analysis template is continuously optimized using the generated output to improve future analyses.

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
    3. Run the script: python main.py
    4. Generated analyses will be in the 'reports/' directory
"""

from dotenv import load_dotenv
import argparse
import sys
from pathlib import Path
import logging

from processing.batch_processing import process_all_transcripts
from utils.config_utils import load_config
from utils.env_utils import check_env_vars, check_pandoc_installed, setup_logging
from utils.file_utils import ensure_reports_dir, get_client, load_analysis_template


# --- Main Entry Point ---
def main():
    """
    Main execution function for MCEM Interview Processing.

    Steps performed:
        1. Sets up logging for the application.
        2. Loads environment variables from .env for secure configuration.
        3. Loads YAML configuration from config.yaml, expanding env vars.
        4. Validates required environment variables and Pandoc installation.
        5. Initializes Azure OpenAI client for transcript analysis.
        6. Ensures the output directory for reports exists.
        7. Loads the analysis template as specified in config or CLI.
        8. Processes all .txt files in the transcripts directory, generating Markdown and Word outputs.
    """
    parser = argparse.ArgumentParser(
        description="""
        MCEM Interview Processing Script

        This tool analyzes qualitative interview or survey transcripts using Azure OpenAI (GPT-4) and a customizable template (default: MCEM framework).
        It extracts key insights, direct quotes, and metrics, and generates structured, business-ready reports in Markdown and Word formats.
        You can specify the input folder, output folder, and template file for maximum flexibility.
        """
    )
    parser.add_argument('--input', '-i', default=None, help='Input folder containing transcript .txt files (default: transcripts/)')
    parser.add_argument('--output', '-o', default=None, help='Output folder for reports (default: reports/)')
    parser.add_argument('--template', '-t', default=None, help='Template file to use for analysis (default: from config or AnalysisTemplate.txt)')
    parser.add_argument('--log-level', default='STANDARD', choices=['STANDARD', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help=(
                            "Set the logging level. 'STANDARD' (default) shows process steps and transcript names; "
                            "'DEBUG'/'INFO' show more detail; 'ERROR' only shows errors."
                        ))
    args = parser.parse_args()

    # Set up STANDARD log level if selected
    STANDARD_LEVEL = 25
    if not hasattr(logging, 'STANDARD'):
        logging.addLevelName(STANDARD_LEVEL, 'STANDARD')
        def standard(self, message, *args, **kws):
            if self.isEnabledFor(STANDARD_LEVEL):
                self._log(STANDARD_LEVEL, message, args, **kws)
        logging.Logger.standard = standard

    setup_logging(level=args.log_level)  # Configure logging to stdout with user-selected level
    logger = logging.getLogger()
    load_dotenv()  # Load .env first so env vars are available for config expansion
    config = load_config()  # Load YAML config with env var expansion
    check_env_vars([
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT"
    ])  # Ensure all required Azure OpenAI env vars are set
    check_pandoc_installed()  # Ensure Pandoc is available for docx conversion
    client = get_client()  # Create Azure OpenAI client

    # Determine input/output/template from CLI or config
    input_dir = args.input or config.get('processing', {}).get('input_dir', 'transcripts')
    output_dir = args.output or config.get('processing', {}).get('output_dir', 'reports')
    template_path = args.template or config.get('processing', {}).get('template_path', 'AnalysisTemplate.txt')

    reports_dir = ensure_reports_dir(Path(output_dir))
    template = load_analysis_template(template_path)  # Load analysis template

    # Process all transcripts in the input directory using the batch processor
    process_all_transcripts(client, template, reports_dir, input_dir=input_dir, template_path=template_path)

    logging.info("Step 3: LLM Self-Check & Validation - AI self-validation complete for all transcripts")
    logging.info("Step 4: Human Review & Approval - Please review the generated reports in '%s' for accuracy, context, and completeness before sharing.", output_dir)
    logging.info("Step 5: Finalized, Shareable Report - Reports are ready in Markdown and Word formats.")


if __name__ == "__main__":
    main()
from openai import AzureOpenAI
import os
from pathlib import Path
import tiktoken
import logging
import sys

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken for GPT-4.
    Args:
        text (str): The text to count tokens for.
    Returns:
        int: The number of tokens in the text.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def get_client() -> AzureOpenAI:
    """Create and return an Azure OpenAI client using environment variables.
    Returns:
        AzureOpenAI: The initialized Azure OpenAI client.
    """
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

def load_analysis_template(template_path: str = "AnalysisTemplate.txt") -> str:
    """Load the analysis template from file.
    Args:
        template_path (str): Path to the template file.
    Returns:
        str: The contents of the template file.
    Raises:
        SystemExit: If the template file is not found.
    """
    try:
        return Path(template_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        logging.error(f"{template_path} not found.")
        sys.exit(1)

def ensure_reports_dir(reports_dir: Path = Path("./reports")) -> Path:
    """Ensure the reports directory exists and return its Path.
    Args:
        reports_dir (Path): The directory to ensure exists.
    Returns:
        Path: The ensured reports directory path.
    """
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

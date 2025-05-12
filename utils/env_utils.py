import logging
import sys
from shutil import which
from typing import List
import os

def setup_logging() -> None:
    """Set up logging configuration for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def check_env_vars(required_vars: List[str]) -> None:
    """Check for required environment variables and exit if any are missing.
    Args:
        required_vars (List[str]): List of required environment variable names.
    """
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logging.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

def check_pandoc_installed() -> None:
    """Check if Pandoc is installed and available in PATH. Exit if not found."""
    if which("pandoc") is None:
        logging.error("Pandoc is not installed or not in PATH. Please install Pandoc to enable Word conversion.")
        sys.exit(1)

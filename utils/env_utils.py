import logging
import sys
import os
from shutil import which
from typing import List

# Define STANDARD log level
STANDARD_LEVEL = 25
if not hasattr(logging, 'STANDARD'):
    logging.addLevelName(STANDARD_LEVEL, 'STANDARD')
    def standard(self, message, *args, **kws):
        if self.isEnabledFor(STANDARD_LEVEL):
            self._log(STANDARD_LEVEL, message, args, **kws)
    logging.Logger.standard = standard

# TQL-style progress bar for pipeline steps
PIPELINE_STEPS = [
    "Preparing Analysis",  # Step 0
    "Transcript Collection",
    "Automated LLM Analysis",
    "LLM Self-Check & Validation",
    "Human Review & Approval",
    "Finalized, Shareable Report"
]

def show_progress_bar(current_step_idx: int, total_steps: int = 6, transcript_name: str = None, extra: str = None):
    bar = "[" + "=" * (current_step_idx + 1) + ">" + "." * (total_steps - current_step_idx - 1) + "]"
    step_name = PIPELINE_STEPS[current_step_idx]
    msg = f"{bar} {current_step_idx+1}/{total_steps} {step_name}"
    if transcript_name:
        msg += f" | Transcript: {transcript_name}"
    if extra:
        msg += f" | {extra}"
    logger = logging.getLogger()
    if logger.getEffectiveLevel() == STANDARD_LEVEL:
        logger.log(STANDARD_LEVEL, msg)


def setup_logging(level="STANDARD") -> None:
    """
    Set up logging configuration for the application.
    Logs are output to stdout with the specified level and a standard format.
    If level is STANDARD, suppress INFO messages and use the progress bar for pipeline steps.

    Args:
        level (str): Logging level as a string (e.g., 'STANDARD', 'DEBUG', 'INFO').
    """
    if level.upper() == "STANDARD":
        loglevel = STANDARD_LEVEL
    else:
        loglevel = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=loglevel,
        format="[%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def check_env_vars(required_vars: List[str]) -> None:
    """
    Check for required environment variables and exit if any are missing.

    Args:
        required_vars (List[str]): List of required environment variable names.

    Exits the program with an error if any required variable is missing.
    """
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logging.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)


def check_pandoc_installed() -> None:
    """
    Check if Pandoc is installed and available in PATH. Exit if not found.

    Exits the program with an error if Pandoc is not found in the system PATH.
    """
    if which("pandoc") is None:
        logging.error("Pandoc is not installed or not in PATH. Please install Pandoc to enable Word conversion.")
        sys.exit(1)


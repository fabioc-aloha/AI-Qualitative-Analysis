import logging
from pathlib import Path
import subprocess


def convert_markdown_to_docx(md_file: Path, docx_file: Path) -> None:
    """
    Convert a Markdown file to a Word document using Pandoc.

    This function calls Pandoc via subprocess to convert a Markdown (.md) file
    to a Word (.docx) document. Logs success or errors.

    Args:
        md_file (Path): Path to the Markdown file.
        docx_file (Path): Path to the output Word document.
    """
    cmd = [
        "pandoc",
        str(md_file),
        "-f", "markdown",
        "-t", "docx",
        "-o", str(docx_file)
    ]
    try:
        subprocess.run(cmd, check=True)
        logging.info(f"Word document saved to {docx_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting to Word document: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error during conversion: {str(e)}")

# Ensure this file is in the 'conversion' folder for proper imports.

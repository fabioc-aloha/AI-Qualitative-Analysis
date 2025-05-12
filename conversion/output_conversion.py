import logging
from pathlib import Path

def convert_markdown_to_docx(md_file: Path, docx_file: Path) -> None:
    """
    Convert a Markdown file to a Word document using Pandoc.
    Args:
        md_file (Path): Path to the Markdown file.
        docx_file (Path): Path to the output Word document.
    """
    import subprocess
    cmd = ["pandoc", str(md_file), "-f", "markdown", "-t", "docx", "-o", str(docx_file)]
    try:
        subprocess.run(cmd, check=True)
        logging.info(f"Word document saved to {docx_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting to Word document: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error during conversion: {str(e)}")

# No import changes needed, but ensure this file is in the 'conversion' folder.

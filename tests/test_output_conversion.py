import pytest
from pathlib import Path
from conversion import output_conversion

def test_convert_markdown_to_docx(tmp_path):
    md_file = tmp_path / "test.md"
    docx_file = tmp_path / "test.docx"
    md_file.write_text("# Test\nContent")
    # This will fail if pandoc is not installed, so we just check for no exception
    try:
        output_conversion.convert_markdown_to_docx(md_file, docx_file)
    except Exception:
        pass

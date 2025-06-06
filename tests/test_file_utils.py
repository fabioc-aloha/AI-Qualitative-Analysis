import pytest
from utils import file_utils
from pathlib import Path

def test_count_tokens():
    text = "Hello world!"
    tokens = file_utils.count_tokens(text)
    assert isinstance(tokens, int)
    assert tokens > 0

def test_ensure_reports_dir(tmp_path):
    reports_dir = tmp_path / "reports"
    result = file_utils.ensure_reports_dir(reports_dir)
    assert result.exists()
    assert result.is_dir()

def test_load_analysis_template(tmp_path):
    template_file = tmp_path / "template.txt"
    template_file.write_text("Sample template content.")
    content = file_utils.load_analysis_template(str(template_file))
    assert content == "Sample template content."

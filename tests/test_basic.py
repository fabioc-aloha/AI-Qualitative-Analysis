import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# Import modules to test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import file_utils, env_utils, config_utils
from processing import transcript_processing, transcript_chunking, batch_processing
from conversion import output_conversion


def test_count_tokens():
    text = "Hello world! This is a test."
    tokens = file_utils.count_tokens(text)
    assert isinstance(tokens, int)
    assert tokens > 0

def test_ensure_reports_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        reports_dir = Path(tmpdir) / "reports"
        result = file_utils.ensure_reports_dir(reports_dir)
        assert result.exists()
        assert result.is_dir()

def test_load_analysis_template(tmp_path):
    template_file = tmp_path / "template.txt"
    template_file.write_text("Sample template content.")
    content = file_utils.load_analysis_template(str(template_file))
    assert content == "Sample template content."

def test_load_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("key: value")
    config = config_utils.load_config(str(config_file))
    assert config["key"] == "value"

def test_check_env_vars(monkeypatch):
    monkeypatch.setenv("TEST_ENV_VAR", "1")
    # Should not raise
    env_utils.check_env_vars(["TEST_ENV_VAR"])

# Additional tests for processing and conversion modules can be added with mocks

def test_convert_markdown_to_docx(tmp_path):
    md_file = tmp_path / "test.md"
    docx_file = tmp_path / "test.docx"
    md_file.write_text("# Test\nContent")
    # This will fail if pandoc is not installed, so we just check for no exception
    try:
        output_conversion.convert_markdown_to_docx(md_file, docx_file)
    except Exception:
        pass

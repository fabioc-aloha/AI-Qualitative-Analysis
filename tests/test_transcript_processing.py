import pytest
from pathlib import Path
from unittest.mock import MagicMock
from processing import transcript_processing


def test_process_transcript_handles_missing_file(tmp_path):
    # Should return None if file does not exist
    fake_path = tmp_path / "does_not_exist.txt"
    client = MagicMock()
    template = "Template"
    result = transcript_processing.process_transcript(fake_path, template, client)
    assert result is None

# More advanced tests would require mocking AzureOpenAI and file contents

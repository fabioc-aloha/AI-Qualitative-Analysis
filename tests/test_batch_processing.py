import pytest
from pathlib import Path
from unittest.mock import MagicMock
from processing import batch_processing

def test_process_all_transcripts_empty(tmp_path, monkeypatch):
    # Should not raise if transcripts folder is empty
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Mock analysis result"
    client.chat.completions.create.return_value = mock_response
    template = "Template"
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    # Create an empty transcripts directory
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    batch_processing.process_all_transcripts(client, template, reports_dir)

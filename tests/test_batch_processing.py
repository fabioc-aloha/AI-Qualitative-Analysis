import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from processing import batch_processing
import os

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

def test_old_report_files_deleted(tmp_path, monkeypatch):
    # Create dummy old report files
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    transcript_file = tmp_path / "transcript.txt"
    transcript_file.write_text("Transcript")
    for ext in ["_analysis.md", "_analysis.docx", "_llm_validation.md"]:
        old_file = reports_dir / f"transcript{ext}"
        old_file.write_text("old content")
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Mock analysis result"
    client.chat.completions.create.return_value = mock_response
    # Place transcript in transcripts dir
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()
    transcript_path = transcripts_dir / "transcript.txt"
    transcript_path.write_text("Transcript")
    monkeypatch.chdir(tmp_path)
    batch_processing.process_all_transcripts(client, "Template", reports_dir, input_dir=str(transcripts_dir))
    # Old files should be deleted and replaced
    for ext in ["_analysis.md", "_llm_validation.md"]:
        new_file = reports_dir / f"transcript{ext}"
        assert new_file.exists()
        assert new_file.read_text() != "old content"
    # For .docx, just check existence
    docx_file = reports_dir / "transcript_analysis.docx"
    assert docx_file.exists()

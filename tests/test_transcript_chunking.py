#!/usr/bin/env python3
"""Tests for the transcript chunking module"""
import os
from unittest.mock import MagicMock, patch

import pytest

from processing import transcript_chunking


@pytest.fixture
def mock_client():
    """Fixture to provide a mock Azure OpenAI client"""
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Mock analysis result"
    client.chat.completions.create.return_value = mock_response
    return client


def test_process_large_transcript_single_chunk(mock_client):
    """Test processing a transcript that fits in a single chunk"""
    # Prepare test data
    transcript = "Short transcript content"
    template = "Analysis template"
    
    # Process the transcript
    result = transcript_chunking.process_large_transcript(transcript, template, mock_client)
    
    # Verify the result
    assert result == "Mock analysis result"
    
    # Verify the client was called correctly
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args['messages'][0]['role'] == 'system'
    assert call_args['messages'][1]['role'] == 'user'
    assert call_args['messages'][1]['content'] == f"{template}\n\nTRANSCRIPT SEGMENT 1/1:\n{transcript}"


def test_process_large_transcript_multiple_chunks(mock_client):
    """Test processing a transcript that requires multiple chunks"""
    # Generate enough tokens to cause chunking (chunk size in module is 80000)
    token_encoding = "x" * 100000  # This will exceed chunk_size tokens
    template = "Analysis template"
    
    # Process the large text
    result = transcript_chunking.process_large_transcript(token_encoding, template, mock_client)
    
    # Verify the result
    assert result == "Mock analysis result"
    
    # Verify that we made both chunk analysis calls and a consolidation call
    assert mock_client.chat.completions.create.call_count >= 2  # At least one chunk and consolidation
    
    # Verify the final call was for consolidation
    last_call_args = mock_client.chat.completions.create.call_args[1]
    assert "consolidating" in last_call_args['messages'][0]['content'].lower()


def test_process_large_transcript_chunk_error(mock_client):
    """Test handling of errors during chunk processing"""
    # Use a smaller text that won't be chunked
    text = "Test transcript"
    template = "Analysis template"
    
    # Make the first call fail but second call succeed
    mock_client.chat.completions.create.side_effect = [
        Exception("Test error"),
        MagicMock(choices=[MagicMock(message=MagicMock(content="Mock analysis result"))])
    ]
    
    # Process the transcript
    result = transcript_chunking.process_large_transcript(text, template, mock_client)
    
    # Since there's only one chunk and it failed, result should be None
    assert result is None


def test_process_large_transcript_consolidation_error(mock_client):
    """Test handling of errors during result consolidation"""
    # Generate enough tokens to cause chunking (chunk size in module is 80000)
    token_encoding = "x" * 100000
    template = "Analysis template"
    
    # Create responses for chunks and make consolidation fail
    chunk_response = MagicMock()
    chunk_response.choices[0].message.content = "Mock chunk result"
    
    def side_effect(*args, **kwargs):
        messages = kwargs.get('messages', [])
        if any('consolidating' in msg.get('content', '').lower() for msg in messages):
            raise Exception("Consolidation error")
        return chunk_response
    
    mock_client.chat.completions.create.side_effect = side_effect
    
    # Process the large transcript
    result = transcript_chunking.process_large_transcript(token_encoding, template, mock_client)
    
    # When consolidation fails, we should get concatenated chunks
    assert result == "Mock chunk result\n\n---\n\nMock chunk result"


def test_process_large_transcript_all_chunks_fail(mock_client):
    """Test handling of all chunk processing attempts failing"""
    # Prepare test data
    transcript = "Test content"
    template = "Analysis template"
    
    # Make all API calls fail
    mock_client.chat.completions.create.side_effect = Exception("Test error")
    
    # Process the transcript
    result = transcript_chunking.process_large_transcript(transcript, template, mock_client)
    
    # Verify we got None when all processing failed
    assert result is None


@patch.dict(os.environ, {'AZURE_OPENAI_DEPLOYMENT': 'test-deployment'})
def test_process_large_transcript_uses_environment_deployment(mock_client):
    """Test that the correct deployment is used from environment variables"""
    # Prepare test data
    transcript = "Test content"
    template = "Analysis template"
    
    # Process the transcript
    transcript_chunking.process_large_transcript(transcript, template, mock_client)
    
    # Verify the deployment was passed correctly
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args['model'] == 'test-deployment'

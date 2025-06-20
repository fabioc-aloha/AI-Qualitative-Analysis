#!/usr/bin/env python3
"""Tests for the main script main.py"""
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_dependencies():
    """Fixture to mock all dependencies of the main script"""
    with patch('main.load_dotenv') as mock_load_dotenv, \
         patch('main.load_config') as mock_load_config, \
         patch('main.check_env_vars') as mock_check_env_vars, \
         patch('main.check_pandoc_installed') as mock_check_pandoc, \
         patch('main.get_client') as mock_get_client, \
         patch('main.ensure_reports_dir') as mock_ensure_reports_dir, \
         patch('main.load_analysis_template') as mock_load_template, \
         patch('main.process_all_transcripts') as mock_process_all:
        # Set up mock return values
        mock_load_config.return_value = {'processing': {'template_path': 'AnalysisTemplate.txt'}}
        mock_get_client.return_value = MagicMock()
        mock_ensure_reports_dir.return_value = Path('./reports')
        mock_load_template.return_value = "Test template"
        yield {
            'load_dotenv': mock_load_dotenv,
            'load_config': mock_load_config,
            'check_env_vars': mock_check_env_vars,
            'check_pandoc': mock_check_pandoc,
            'get_client': mock_get_client,
            'ensure_reports_dir': mock_ensure_reports_dir,
            'load_template': mock_load_template,
            'process_all': mock_process_all
        }


def test_main_success(mock_dependencies):
    """Test successful execution of the main function"""
    import sys
    from main import main
    # Patch sys.argv so argparse doesn't see pytest args
    with patch.object(sys, 'argv', ['main.py']):
        main()
    # Verify all dependencies were called
    mock_dependencies['load_dotenv'].assert_called_once()
    mock_dependencies['load_config'].assert_called_once()
    mock_dependencies['check_env_vars'].assert_called_once_with([
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT"
    ])
    mock_dependencies['check_pandoc'].assert_called_once()
    mock_dependencies['get_client'].assert_called_once()
    mock_dependencies['ensure_reports_dir'].assert_called_once()
    mock_dependencies['load_template'].assert_called_once_with('AnalysisTemplate.txt')
    mock_dependencies['process_all'].assert_called_once_with(
        mock_dependencies['get_client'].return_value,
        mock_dependencies['load_template'].return_value,
        mock_dependencies['ensure_reports_dir'].return_value,
        input_dir='transcripts',
        template_path='AnalysisTemplate.txt'
    )


def test_main_config_missing_template_path(mock_dependencies):
    """Test main function when template_path is missing from config"""
    import sys
    from main import main
    # Set up config without template_path
    mock_dependencies['load_config'].return_value = {'processing': {}}
    # Patch sys.argv so argparse doesn't see pytest args
    with patch.object(sys, 'argv', ['main.py']):
        main()

    # Verify default template path is used
    mock_dependencies['load_template'].assert_called_once_with('AnalysisTemplate.txt')


def test_main_env_vars_missing(mock_dependencies):
    """Test main function when environment variables are missing"""
    import sys
    from main import main

    # Make check_env_vars raise SystemExit
    mock_dependencies['check_env_vars'].side_effect = SystemExit(1)

    # Run the main function and expect it to exit
    with patch.object(sys, 'argv', ['main.py']):
        with pytest.raises(SystemExit):
            main()

    # Verify we checked env vars but didn't proceed further
    mock_dependencies['check_env_vars'].assert_called_once()
    mock_dependencies['get_client'].assert_not_called()


def test_main_pandoc_missing(mock_dependencies):
    """Test main function when Pandoc is not installed"""
    import sys
    from main import main

    # Make check_pandoc_installed raise SystemExit
    mock_dependencies['check_pandoc'].side_effect = SystemExit(1)

    # Run the main function and expect it to exit
    with patch.object(sys, 'argv', ['main.py']):
        with pytest.raises(SystemExit):
            main()

    # Verify we checked for Pandoc but didn't proceed further
    mock_dependencies['check_pandoc'].assert_called_once()
    mock_dependencies['get_client'].assert_not_called()

import pytest
from utils import env_utils


def test_setup_logging():
    # Should not raise
    env_utils.setup_logging()


def test_check_pandoc_installed(monkeypatch):
    # Simulate pandoc not installed
    monkeypatch.setattr("utils.env_utils.which", lambda x: None)
    with pytest.raises(SystemExit):
        env_utils.check_pandoc_installed()

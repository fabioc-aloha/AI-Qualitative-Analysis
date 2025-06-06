import pytest
from utils import config_utils
from pathlib import Path

def test_load_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("foo: bar")
    config = config_utils.load_config(str(config_file))
    assert config["foo"] == "bar"

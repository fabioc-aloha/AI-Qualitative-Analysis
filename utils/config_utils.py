import os
import yaml
from typing import Any, Dict


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from a YAML file, expanding environment variables.

    Args:
        config_path (str): Path to the YAML config file.
    Returns:
        Dict[str, Any]: The loaded configuration dictionary with env vars expanded.
    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = f.read()
        # Expand environment variables in the YAML (e.g., ${VAR})
        raw = os.path.expandvars(raw)
        config = yaml.safe_load(raw)
    return config

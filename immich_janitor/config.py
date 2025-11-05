"""Configuration management."""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config():
    """Load configuration from .env file if it exists."""
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    return {
        "api_url": os.getenv("IMMICH_API_URL"),
        "api_key": os.getenv("IMMICH_API_KEY"),
    }

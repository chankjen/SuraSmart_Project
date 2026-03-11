# utils/helpers.py
"""
Sura Smart Helper Functions
Common utility functions
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


def load_json_file(file_path: str) -> Dict:
    """Load JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json_file(file_path: str, data: Dict) -> None:
    """Save data to JSON file"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string"""
    return datetime.fromisoformat(timestamp_str)


def get_env_variable(name: str, default: Any = None) -> Any:
    """Get environment variable with default"""
    return os.environ.get(name, default)


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'
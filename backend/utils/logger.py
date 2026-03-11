# utils/logger.py
"""
Sura Smart Logger Configuration
TRD Section 7.4: Monitoring
"""

import logging
import os
from pathlib import Path
from datetime import datetime


def get_logger(name: str, level: str = None) -> logging.Logger:
    """
    Get configured logger.
    
    TRD 7.4: Comprehensive monitoring
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    # Set level
    log_level = level or os.environ.get('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create log directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # File handler
    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
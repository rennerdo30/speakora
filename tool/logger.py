import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 10485760,
    backup_count: int = 5,
    console_enabled: bool = True,
) -> logging.Logger:
    """Centralized logging setup."""
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )

    if console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

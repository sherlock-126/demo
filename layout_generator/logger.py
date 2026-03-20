"""
Logging configuration for layout generator
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(
            log_dir / "layout_generator.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)

    return logger
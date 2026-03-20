"""
Logging configuration for the content generator
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str = "content_generator",
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_rich: bool = True
) -> logging.Logger:
    """
    Set up a logger with rich formatting and optional file output

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        use_rich: Whether to use rich formatting for console output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with rich formatting
    if use_rich:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True
        )
        console_handler.setFormatter(
            logging.Formatter("%(message)s", datefmt="[%X]")
        )
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create dated log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file_path = log_path.parent / f"{today}_{log_path.name}"

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(file_handler)

    return logger


# Create default logger instance
# Lazy initialization to avoid circular import
logger = None

def get_logger():
    global logger
    if logger is None:
        from .config import config
        logger = setup_logger(
            level=config.log_level,
            log_file=config.log_file if not config.is_production else None
        )
    return logger

# For backward compatibility
logger = get_logger()


def log_generation_start(topic: str, num_slides: int, language: str):
    """Log the start of a script generation"""
    logger.info(
        f"Starting generation: topic='{topic}', "
        f"slides={num_slides}, language={language}"
    )


def log_generation_success(topic: str, tokens_used: int, duration: float):
    """Log successful script generation"""
    logger.info(
        f"Generation successful: topic='{topic}', "
        f"tokens={tokens_used}, duration={duration:.2f}s"
    )


def log_generation_error(topic: str, error: str):
    """Log generation error"""
    logger.error(f"Generation failed: topic='{topic}', error={error}")


def log_api_retry(attempt: int, max_attempts: int, error: str):
    """Log API retry attempt"""
    logger.warning(
        f"API retry {attempt}/{max_attempts}: {error}"
    )
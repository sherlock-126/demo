"""File handling utilities for Streamlit application."""

import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def create_directory(path: str) -> Path:
    """Create directory if it doesn't exist.

    Args:
        path: Directory path to create

    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ensured: {dir_path}")
    return dir_path


def clean_directory(path: str, exclude_patterns: List[str] = None) -> None:
    """Clean directory contents while preserving the directory itself.

    Args:
        path: Directory path to clean
        exclude_patterns: List of filename patterns to exclude from deletion
    """
    dir_path = Path(path)
    if not dir_path.exists():
        return

    exclude_patterns = exclude_patterns or []

    for item in dir_path.iterdir():
        # Check if item should be excluded
        if any(pattern in str(item) for pattern in exclude_patterns):
            continue

        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
            logger.debug(f"Removed: {item}")
        except Exception as e:
            logger.error(f"Failed to remove {item}: {e}")


def get_file_list(directory: str, extensions: List[str] = None) -> List[Path]:
    """Get list of files in directory with optional extension filter.

    Args:
        directory: Directory path to scan
        extensions: List of file extensions to filter (e.g., ['.png', '.jpg'])

    Returns:
        List of Path objects for matching files
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    files = []
    for item in sorted(dir_path.iterdir()):
        if item.is_file():
            if extensions is None or item.suffix.lower() in extensions:
                files.append(item)

    return files


def create_zip_archive(files: List[Path], output_path: str) -> Path:
    """Create ZIP archive from list of files.

    Args:
        files: List of file paths to archive
        output_path: Output ZIP file path

    Returns:
        Path to created ZIP file
    """
    zip_path = Path(output_path)

    # Add timestamp if file exists
    if zip_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = zip_path.with_stem(f"{zip_path.stem}_{timestamp}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            if file_path.exists():
                arcname = file_path.name  # Use filename only
                zipf.write(file_path, arcname)
                logger.debug(f"Added to archive: {file_path.name}")

    logger.info(f"Created ZIP archive: {zip_path}")
    return zip_path


def safe_file_operation(func):
    """Decorator for safe file operations with error handling.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            raise PermissionError(f"Permission denied: Check file permissions")
        except IOError as e:
            logger.error(f"I/O error: {e}")
            raise IOError(f"File operation failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}")
            raise Exception(f"Unexpected error: {e}")
    return wrapper


def get_file_size(path: str) -> int:
    """Get file size in bytes.

    Args:
        path: File path

    Returns:
        File size in bytes
    """
    return Path(path).stat().st_size if Path(path).exists() else 0


def format_file_size(size_bytes: int) -> str:
    """Format file size to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
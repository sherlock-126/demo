"""Input validation utilities for Streamlit application."""

import re
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """Validate OpenAI API key format.

    Args:
        api_key: API key to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"

    if not api_key.startswith("sk-"):
        return False, "Invalid API key format (should start with 'sk-')"

    if len(api_key) < 20:
        return False, "API key seems too short"

    return True, ""


def validate_topic(topic: str, min_length: int = 10, max_length: int = 500) -> Tuple[bool, str]:
    """Validate topic input.

    Args:
        topic: Topic text to validate
        min_length: Minimum character length
        max_length: Maximum character length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not topic:
        return False, "Topic is required"

    topic = topic.strip()

    if len(topic) < min_length:
        return False, f"Topic must be at least {min_length} characters"

    if len(topic) > max_length:
        return False, f"Topic must not exceed {max_length} characters"

    # Check for meaningful content (not just special characters)
    if not re.search(r'[a-zA-Z0-9\u0080-\uFFFF]{3,}', topic):
        return False, "Topic must contain meaningful text"

    return True, ""


def validate_file_format(file_path: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
    """Validate file format based on extension.

    Args:
        file_path: File path to validate
        allowed_extensions: List of allowed extensions (e.g., ['.mp3', '.wav'])

    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    if not path.is_file():
        return False, f"Not a file: {file_path}"

    extension = path.suffix.lower()
    if extension not in allowed_extensions:
        return False, f"Invalid file format. Allowed: {', '.join(allowed_extensions)}"

    return True, ""


def check_file_size(file_path: str, max_size_mb: float = 100) -> Tuple[bool, str]:
    """Check if file size is within limits.

    Args:
        file_path: File path to check
        max_size_mb: Maximum size in megabytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    size_mb = path.stat().st_size / (1024 * 1024)

    if size_mb > max_size_mb:
        return False, f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)"

    return True, ""


def validate_num_slides(num_slides: int) -> Tuple[bool, str]:
    """Validate number of slides.

    Args:
        num_slides: Number of slides

    Returns:
        Tuple of (is_valid, error_message)
    """
    if num_slides < 3:
        return False, "Minimum 3 slides required"

    if num_slides > 10:
        return False, "Maximum 10 slides allowed"

    return True, ""


def validate_video_duration(num_slides: int, duration_per_slide: float,
                          transition_duration: float) -> Tuple[bool, str, float]:
    """Validate and calculate total video duration.

    Args:
        num_slides: Number of slides
        duration_per_slide: Duration per slide in seconds
        transition_duration: Transition duration in seconds

    Returns:
        Tuple of (is_valid, error_message, total_duration)
    """
    # Calculate total duration: N slides * duration - (N-1) transitions overlap
    total_duration = num_slides * duration_per_slide - (num_slides - 1) * transition_duration

    if total_duration > 60:
        return False, f"Video too long for TikTok: {total_duration:.1f}s (max: 60s)", total_duration

    if total_duration < 5:
        return False, f"Video too short: {total_duration:.1f}s (min: 5s)", total_duration

    return True, "", total_duration
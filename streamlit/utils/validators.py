"""
Input validation utilities
"""

from pathlib import Path


def validate_api_key(api_key):
    """Validate OpenAI API key format"""
    if not api_key:
        return False, "API key is required"

    if not api_key.startswith('sk-'):
        return False, "Invalid API key format (should start with 'sk-')"

    if len(api_key) < 20:
        return False, "API key appears to be too short"

    return True, "API key is valid"


def validate_topic(topic, min_length=10):
    """Validate topic input"""
    if not topic:
        return False, "Topic is required"

    if len(topic) < min_length:
        return False, f"Topic must be at least {min_length} characters"

    return True, "Topic is valid"


def validate_images(image_paths):
    """Validate image paths exist"""
    if not image_paths:
        return False, "No images provided"

    valid_paths = []
    for path in image_paths:
        if Path(path).exists():
            valid_paths.append(path)

    if not valid_paths:
        return False, "No valid image files found"

    return True, f"{len(valid_paths)} valid images found"
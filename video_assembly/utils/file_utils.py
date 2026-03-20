"""
File system utilities
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import re


class FileUtils:
    """File system utility functions"""

    @staticmethod
    def ensure_directory(path: str) -> Path:
        """
        Ensure directory exists

        Args:
            path: Directory path

        Returns:
            Path object
        """
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @staticmethod
    def create_temp_directory(base_path: str = '/tmp') -> Path:
        """
        Create temporary directory

        Args:
            base_path: Base path for temp directory

        Returns:
            Path to temporary directory
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_dir = Path(base_path) / f'video_assembly_{timestamp}'
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    @staticmethod
    def cleanup_temp_directory(path: str):
        """
        Clean up temporary directory

        Args:
            path: Directory to remove
        """
        try:
            if Path(path).exists():
                shutil.rmtree(path)
        except Exception:
            pass  # Ignore cleanup errors

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for filesystem

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        return name + ext

    @staticmethod
    def generate_output_path(
        base_dir: str,
        prefix: str = 'video',
        extension: str = '.mp4'
    ) -> str:
        """
        Generate unique output path

        Args:
            base_dir: Base directory
            prefix: File prefix
            extension: File extension

        Returns:
            Unique file path
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f'{prefix}_{timestamp}{extension}'
        output_path = Path(base_dir) / base_name

        # Add counter if file exists
        counter = 1
        while output_path.exists():
            base_name = f'{prefix}_{timestamp}_{counter}{extension}'
            output_path = Path(base_dir) / base_name
            counter += 1

        return str(output_path)

    @staticmethod
    def get_file_size_readable(file_path: str) -> str:
        """
        Get human-readable file size

        Args:
            file_path: Path to file

        Returns:
            Readable file size string
        """
        try:
            size = Path(file_path).stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f'{size:.2f} {unit}'
                size /= 1024.0
            return f'{size:.2f} TB'
        except Exception:
            return 'Unknown'

    @staticmethod
    def check_disk_space(path: str, required_mb: int = 500) -> bool:
        """
        Check if enough disk space available

        Args:
            path: Path to check
            required_mb: Required space in MB

        Returns:
            True if enough space available
        """
        try:
            stat = shutil.disk_usage(path)
            available_mb = stat.free / (1024 * 1024)
            return available_mb >= required_mb
        except Exception:
            return True  # Assume enough space if check fails
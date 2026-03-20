"""
File handling utilities
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime, timedelta


def create_output_dir(dir_name="output"):
    """Create output directory if it doesn't exist"""
    output_dir = Path(dir_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def cleanup_old_files(directory, days=7, pattern="*"):
    """Remove files older than specified days"""
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0

    cutoff = datetime.now() - timedelta(days=days)
    removed = 0

    for file in dir_path.glob(pattern):
        if file.is_file():
            file_time = datetime.fromtimestamp(file.stat().st_mtime)
            if file_time < cutoff:
                file.unlink()
                removed += 1

    return removed


def create_zip_archive(files, output_name=None):
    """Create ZIP archive from list of files"""
    if not files:
        return None

    if not output_name:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"archive_{timestamp}.zip"

    output_path = Path("output") / output_name

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            if Path(file_path).exists():
                zipf.write(file_path, Path(file_path).name)

    return str(output_path) if output_path.exists() else None
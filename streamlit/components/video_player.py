"""Video player component for displaying generated videos."""

import streamlit as st
from pathlib import Path
from typing import Optional
import logging
import base64

logger = logging.getLogger(__name__)


def render_video_player(video_path: Path, autoplay: bool = False) -> None:
    """Render video player with controls.

    Args:
        video_path: Path to video file
        autoplay: Whether to autoplay the video
    """
    if not video_path or not video_path.exists():
        st.error("Video file not found")
        return

    try:
        # Display video using Streamlit's native video player
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()

        st.video(video_bytes)

        # Video metadata
        size_mb = video_path.stat().st_size / (1024 * 1024)
        st.caption(f"📹 {video_path.name} • {size_mb:.1f}MB")

    except Exception as e:
        st.error(f"Failed to load video: {e}")
        logger.error(f"Failed to load {video_path}: {e}")


def create_download_button(file_path: Path, label: str = "Download",
                         mime_type: str = None) -> None:
    """Create a download button for any file.

    Args:
        file_path: Path to file
        label: Button label
        mime_type: MIME type of file
    """
    if not file_path or not file_path.exists():
        st.error("File not found")
        return

    # Determine MIME type
    if mime_type is None:
        extension = file_path.suffix.lower()
        mime_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/quicktime',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.zip': 'application/zip',
            '.json': 'application/json'
        }
        mime_type = mime_types.get(extension, 'application/octet-stream')

    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        # File size
        size_mb = len(file_bytes) / (1024 * 1024)
        button_label = f"{label} ({size_mb:.1f}MB)"

        st.download_button(
            label=button_label,
            data=file_bytes,
            file_name=file_path.name,
            mime=mime_type,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Failed to create download: {e}")
        logger.error(f"Failed to create download for {file_path}: {e}")


def display_video_info(video_path: Path) -> None:
    """Display video file information.

    Args:
        video_path: Path to video file
    """
    if not video_path or not video_path.exists():
        st.warning("No video information available")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        size_mb = video_path.stat().st_size / (1024 * 1024)
        st.metric("File Size", f"{size_mb:.1f}MB")

    with col2:
        st.metric("Format", video_path.suffix.upper()[1:])

    with col3:
        st.metric("Status", "✅ Ready")


def create_video_preview_html(video_path: Path, width: int = 360) -> str:
    """Create HTML for embedded video preview.

    Args:
        video_path: Path to video file
        width: Preview width in pixels

    Returns:
        HTML string for video embed
    """
    if not video_path.exists():
        return "<p>Video not found</p>"

    # Read video and encode to base64
    try:
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode()

        html = f'''
        <video width="{width}" controls>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        '''
        return html

    except Exception as e:
        logger.error(f"Failed to create video preview: {e}")
        return f"<p>Error loading video: {e}</p>"
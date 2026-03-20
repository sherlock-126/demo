"""
Video player component for displaying generated videos
"""

import streamlit as st
from pathlib import Path
from datetime import datetime


def display_video(video_path, autoplay=False):
    """Display video with player controls"""
    if not video_path or not Path(video_path).exists():
        st.error("Video file not found")
        return False

    try:
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)

        # Display video info
        file_size = Path(video_path).stat().st_size / (1024 * 1024)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("File Size", f"{file_size:.2f} MB")
        with col2:
            st.metric("Format", "MP4")
        with col3:
            st.metric("Resolution", "1080x1920")

        return True

    except Exception as e:
        st.error(f"Failed to display video: {e}")
        return False


def video_download_button(video_path, button_text="⬇️ Download Video"):
    """Create download button for video"""
    if not video_path or not Path(video_path).exists():
        st.error("No video available for download")
        return False

    try:
        with open(video_path, 'rb') as f:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return st.download_button(
                button_text,
                data=f.read(),
                file_name=f"tiktok_video_{timestamp}.mp4",
                mime="video/mp4",
                use_container_width=True,
                type="primary"
            )
    except Exception as e:
        st.error(f"Failed to create download button: {e}")
        return False
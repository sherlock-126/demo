"""Image gallery component for displaying generated images."""

import streamlit as st
from pathlib import Path
from typing import List, Optional
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def render_image_grid(images: List[Path], columns: int = 3,
                     show_download: bool = True) -> None:
    """Render images in a grid layout.

    Args:
        images: List of image file paths
        columns: Number of columns in grid
        show_download: Whether to show download buttons
    """
    if not images:
        st.warning("No images to display")
        return

    # Filter existing files
    valid_images = [img for img in images if img.exists()]

    if not valid_images:
        st.error("No valid image files found")
        return

    st.info(f"📸 Found {len(valid_images)} images")

    # Create grid
    for i in range(0, len(valid_images), columns):
        cols = st.columns(columns)

        for j, col in enumerate(cols):
            if i + j < len(valid_images):
                with col:
                    img_path = valid_images[i + j]
                    _display_image_card(img_path, i + j + 1, show_download)


def _display_image_card(img_path: Path, index: int, show_download: bool = True) -> None:
    """Display single image card with preview and download.

    Args:
        img_path: Path to image file
        index: Image index for labeling
        show_download: Whether to show download button
    """
    try:
        # Load and display image
        img = Image.open(img_path)
        st.image(img, caption=f"Slide {index}", use_container_width=True)

        # Image info
        width, height = img.size
        size_kb = img_path.stat().st_size / 1024
        st.caption(f"{width}x{height} • {size_kb:.1f}KB")

        # Download button
        if show_download:
            with open(img_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download",
                    data=f.read(),
                    file_name=img_path.name,
                    mime="image/png",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Failed to load image: {e}")
        logger.error(f"Failed to load {img_path}: {e}")


def display_image_preview(image_path: Path, max_width: int = 800) -> None:
    """Display single image in preview mode.

    Args:
        image_path: Path to image file
        max_width: Maximum display width in pixels
    """
    if not image_path.exists():
        st.error(f"Image not found: {image_path}")
        return

    try:
        img = Image.open(image_path)

        # Display image
        st.image(img, caption=image_path.name, use_container_width=True)

        # Image metadata
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Width", f"{img.width}px")
        with col2:
            st.metric("Height", f"{img.height}px")
        with col3:
            st.metric("Format", img.format)
        with col4:
            size_kb = image_path.stat().st_size / 1024
            st.metric("Size", f"{size_kb:.1f}KB")

    except Exception as e:
        st.error(f"Failed to preview image: {e}")
        logger.error(f"Failed to preview {image_path}: {e}")


def create_image_selector(images: List[Path]) -> Optional[Path]:
    """Create an image selector widget.

    Args:
        images: List of image paths

    Returns:
        Selected image path or None
    """
    if not images:
        return None

    # Create options
    options = {img.name: img for img in images if img.exists()}

    if not options:
        st.warning("No valid images to select")
        return None

    # Selection widget
    selected_name = st.selectbox(
        "Select an image",
        options=list(options.keys()),
        format_func=lambda x: x
    )

    return options.get(selected_name)
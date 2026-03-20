"""
Image gallery component for displaying generated images
"""

import streamlit as st
from pathlib import Path
from PIL import Image


def display_gallery(image_paths, columns=3):
    """Display images in a grid gallery"""
    if not image_paths:
        st.info("No images to display")
        return

    valid_paths = [p for p in image_paths if Path(p).exists()]

    if not valid_paths:
        st.warning("No valid images found")
        return

    rows = len(valid_paths) // columns + (1 if len(valid_paths) % columns else 0)

    for row in range(rows):
        cols = st.columns(columns)
        for col_idx in range(columns):
            img_idx = row * columns + col_idx
            if img_idx < len(valid_paths):
                with cols[col_idx]:
                    display_image_with_download(valid_paths[img_idx], img_idx + 1)


def display_image_with_download(image_path, index):
    """Display single image with download button"""
    try:
        image = Image.open(image_path)
        st.image(image, caption=f"Slide {index}", use_column_width=True)

        with open(image_path, 'rb') as f:
            st.download_button(
                f"💾 Download",
                data=f.read(),
                file_name=Path(image_path).name,
                mime="image/png",
                key=f"img_download_{index}",
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Failed to load image: {e}")


def create_image_grid(image_paths, selected_callback=None):
    """Create interactive image grid with selection"""
    if not image_paths:
        return None

    valid_paths = [p for p in image_paths if Path(p).exists()]

    # Create selection grid
    selected = st.selectbox(
        "Select Image",
        options=range(len(valid_paths)),
        format_func=lambda x: f"Slide {x + 1}"
    )

    if selected is not None and selected < len(valid_paths):
        image_path = valid_paths[selected]
        image = Image.open(image_path)
        st.image(image, caption=f"Slide {selected + 1}", use_column_width=True)

        if selected_callback:
            selected_callback(image_path, selected)

        return selected

    return None
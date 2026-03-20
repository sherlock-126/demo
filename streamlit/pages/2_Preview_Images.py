"""Page for generating and previewing images."""

import streamlit as st
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    init_session_state,
    get_state,
    set_state,
    create_directory,
    get_file_list,
    create_zip_archive
)
from components import (
    render_image_grid,
    display_image_preview,
    ProgressTracker
)

# Configure logging
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Preview Images - TikTok Generator",
    page_icon="🎨",
    layout="wide"
)

def preview_images_page():
    """Image generation and preview page."""
    init_session_state()

    st.header("🎨 Preview Images")
    st.markdown("Generate and preview images from your script")

    # Check prerequisites
    script_json = get_state('script_json')
    if not script_json:
        st.warning("⚠️ Please generate a script first in the 'Generate Script' page")
        return

    # Tab interface
    tab1, tab2, tab3 = st.tabs(["🎨 Generate Images", "🖼️ Gallery View", "⚙️ Settings"])

    with tab1:
        generate_images_interface()

    with tab2:
        gallery_view_interface()

    with tab3:
        image_settings_interface()


def generate_images_interface():
    """Interface for generating images from script."""
    st.subheader("Generate Images from Script")

    script_json = get_state('script_json')
    slides = script_json.get('slides', [])

    # Display script summary
    st.info(f"📋 Script has {len(slides)} slides ready for image generation")

    # Generation options
    col1, col2 = st.columns(2)

    with col1:
        layout_style = st.selectbox(
            "Layout Style",
            ["Split Screen", "Top-Bottom", "Side by Side"],
            index=0,
            help="Choose the visual layout style"
        )

    with col2:
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Default", "Warm", "Cool", "Monochrome"],
            index=0,
            help="Choose the color palette"
        )

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2, col3 = st.columns(3)

        with col1:
            font_size = st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1)
        with col2:
            include_logo = st.checkbox("Include Logo", value=True)
        with col3:
            include_advice = st.checkbox("Include Advice Text", value=True)

    # Generate button
    if st.button("🚀 Generate All Images", type="primary", use_container_width=True):
        generate_images_from_script(slides, layout_style)

    # Regenerate single slide
    st.divider()
    st.subheader("Regenerate Single Slide")

    slide_options = [f"Slide {i+1}: {slide.get('title', 'Untitled')}" for i, slide in enumerate(slides)]
    selected_slide = st.selectbox(
        "Select slide to regenerate",
        options=range(len(slides)),
        format_func=lambda x: slide_options[x]
    )

    if st.button("🔄 Regenerate Selected Slide"):
        regenerate_single_slide(slides[selected_slide], selected_slide)


def generate_images_from_script(slides, layout_style="Split Screen"):
    """Generate images from script slides."""
    try:
        # Ensure output directory exists
        output_dir = create_directory("output")

        # Import layout generator
        from layout_generator import LayoutGenerator, LayoutConfig

        # Create progress tracker
        progress = ProgressTracker(len(slides) + 1, "Generating Images")
        progress.update(0, "Initializing generator...")

        # Initialize generator
        config = LayoutConfig(
            width=1080,
            height=1920,
            style="split_screen" if layout_style == "Split Screen" else "default"
        )
        generator = LayoutGenerator(config)

        generated_images = []

        # Generate each slide
        for i, slide in enumerate(slides):
            progress.update(i + 1, f"Generating slide {i + 1} of {len(slides)}...")

            # Generate image
            image_path = output_dir / f"slide_{i+1:02d}.png"
            generator.generate_slide(slide, str(image_path))

            if image_path.exists():
                generated_images.append(image_path)

        # Store in session state
        set_state('generated_images', generated_images)
        set_state('generation_status', 'images_ready')

        progress.complete(f"Generated {len(generated_images)} images successfully!")

        # Show preview
        st.success(f"✅ Successfully generated {len(generated_images)} images!")

        # Display first few images
        st.subheader("Preview")
        preview_images = generated_images[:3]
        render_image_grid(preview_images, columns=3, show_download=True)

        if len(generated_images) > 3:
            st.info(f"... and {len(generated_images) - 3} more images. View all in the Gallery tab.")

    except Exception as e:
        st.error(f"Failed to generate images: {str(e)}")
        logger.error(f"Image generation failed: {e}")


def regenerate_single_slide(slide, index):
    """Regenerate a single slide image."""
    try:
        from layout_generator import LayoutGenerator, LayoutConfig

        with st.spinner(f"Regenerating slide {index + 1}..."):
            # Initialize generator
            config = LayoutConfig(width=1080, height=1920)
            generator = LayoutGenerator(config)

            # Generate image
            output_dir = create_directory("output")
            image_path = output_dir / f"slide_{index+1:02d}.png"
            generator.generate_slide(slide, str(image_path))

            st.success(f"✅ Slide {index + 1} regenerated successfully!")

            # Show preview
            if image_path.exists():
                display_image_preview(image_path)

    except Exception as e:
        st.error(f"Failed to regenerate slide: {str(e)}")
        logger.error(f"Slide regeneration failed: {e}")


def gallery_view_interface():
    """Gallery view for generated images."""
    st.subheader("Image Gallery")

    # Get generated images
    generated_images = get_state('generated_images', [])

    if not generated_images:
        # Try to find existing images
        output_dir = Path("output")
        if output_dir.exists():
            generated_images = get_file_list(str(output_dir), ['.png', '.jpg'])
            if generated_images:
                set_state('generated_images', generated_images)

    if not generated_images:
        st.info("No images generated yet. Use the 'Generate Images' tab to create images from your script.")
        return

    # Gallery options
    col1, col2, col3 = st.columns(3)

    with col1:
        columns = st.selectbox("Columns", [2, 3, 4], index=1)

    with col2:
        st.metric("Total Images", len(generated_images))

    with col3:
        if st.button("📥 Download All as ZIP"):
            download_all_images(generated_images)

    # Display gallery
    st.divider()
    render_image_grid(generated_images, columns=columns, show_download=True)


def download_all_images(images):
    """Create ZIP archive of all images."""
    try:
        # Create ZIP file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = create_zip_archive(
            images,
            f"data/tiktok_images_{timestamp}.zip"
        )

        # Offer download
        with open(zip_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Download ZIP ({len(images)} images)",
                data=f.read(),
                file_name=zip_path.name,
                mime="application/zip"
            )

        st.success(f"✅ ZIP archive created: {zip_path.name}")

    except Exception as e:
        st.error(f"Failed to create ZIP: {str(e)}")
        logger.error(f"ZIP creation failed: {e}")


def image_settings_interface():
    """Image generation settings interface."""
    st.subheader("Image Generation Settings")

    # Display current settings
    st.markdown("### Current Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Image Specifications:**
        - Resolution: 1080x1920 (9:16)
        - Format: PNG
        - Layout: Split Screen
        - Font: Default system font
        """)

    with col2:
        st.markdown("""
        **Style Settings:**
        - Background: Gradient
        - Text Color: Auto-contrast
        - Icon Style: Emoji
        - Border: None
        """)

    st.divider()

    # Asset check
    st.subheader("Asset Status")

    assets_dir = Path("assets")
    col1, col2, col3 = st.columns(3)

    with col1:
        fonts_exist = (assets_dir / "fonts").exists() if assets_dir.exists() else False
        if fonts_exist:
            st.success("✅ Fonts available")
        else:
            st.warning("⚠️ Using system fonts")

    with col2:
        icons_exist = (assets_dir / "icons").exists() if assets_dir.exists() else False
        if icons_exist:
            st.success("✅ Icons available")
        else:
            st.info("ℹ️ Using emoji icons")

    with col3:
        logo_exist = (assets_dir / "logo.png").exists() if assets_dir.exists() else False
        if logo_exist:
            st.success("✅ Logo available")
        else:
            st.info("ℹ️ No logo configured")

    # Next steps
    st.divider()
    if get_state('generated_images'):
        st.success("✅ Images are ready!")
        st.info("💡 Go to 'Create Video' page to assemble your TikTok video")


if __name__ == "__main__":
    preview_images_page()
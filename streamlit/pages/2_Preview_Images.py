"""
Page 2: Preview Images
Generate and preview split-screen images from script
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import zipfile
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from layout_generator import LayoutGenerator, LayoutConfig
except ImportError as e:
    st.error(f"Failed to import layout_generator: {e}")
    st.stop()

st.set_page_config(
    page_title="Preview Images",
    page_icon="🖼️",
    layout="wide"
)

def check_script():
    """Check if script exists in session state"""
    if not st.session_state.get('current_script'):
        st.warning("⚠️ No script found. Please generate a script first.")
        if st.button("← Go to Generate Script"):
            st.switch_page("pages/1_Generate_Script.py")
        return False
    return True

def generate_images():
    """Generate images from script using layout_generator"""
    try:
        st.session_state.generation_status = 'generating_images'

        # Initialize generator
        generator = LayoutGenerator()

        # Get script data
        script_data = st.session_state.script_json or st.session_state.current_script
        slides = script_data.get('slides', [])

        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        # Generate timestamp for this batch
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        generated_paths = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, slide in enumerate(slides):
            status_text.text(f"Generating image {idx + 1}/{len(slides)}...")
            progress_bar.progress((idx + 1) / len(slides))

            # Create config for this slide
            config = LayoutConfig(
                title=slide.get('title', ''),
                subtitle=slide.get('subtitle', ''),
                wrong_text=slide.get('wrong', {}).get('text', ''),
                right_text=slide.get('right', {}).get('text', ''),
                wrong_description=slide.get('wrong', {}).get('description', ''),
                right_description=slide.get('right', {}).get('description', '')
            )

            # Generate image
            output_path = output_dir / f"slide_{timestamp}_{idx + 1:02d}.png"
            result = generator.generate(config, str(output_path))

            if result and Path(result.output_path).exists():
                generated_paths.append(str(result.output_path))

        # Store in session state
        st.session_state.generated_images = generated_paths
        st.session_state.generation_status = 'images_complete'

        progress_bar.progress(1.0)
        status_text.text("All images generated successfully!")

        return True

    except Exception as e:
        st.session_state.generation_status = 'error'
        st.session_state.error_log.append(str(e))
        st.error(f"❌ Image generation failed: {e}")
        return False

def create_zip_download(image_paths):
    """Create a ZIP file of all images"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = Path('output') / f'images_{timestamp}.zip'

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for path in image_paths:
            if Path(path).exists():
                zipf.write(path, Path(path).name)

    return str(zip_path)

def display_image_gallery(image_paths):
    """Display images in a grid gallery"""
    if not image_paths:
        return

    # Filter existing paths
    valid_paths = [p for p in image_paths if Path(p).exists()]

    if not valid_paths:
        st.warning("No valid images found")
        return

    # Display in grid
    cols_per_row = 3
    rows = len(valid_paths) // cols_per_row + (1 if len(valid_paths) % cols_per_row else 0)

    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            img_idx = row * cols_per_row + col_idx
            if img_idx < len(valid_paths):
                with cols[col_idx]:
                    img_path = valid_paths[img_idx]

                    # Load and display image
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=f"Slide {img_idx + 1}", use_column_width=True)

                        # Individual download button
                        with open(img_path, 'rb') as f:
                            st.download_button(
                                f"💾 Download",
                                data=f.read(),
                                file_name=Path(img_path).name,
                                mime="image/png",
                                key=f"download_{img_idx}",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Failed to load image: {e}")

def main():
    st.title("🖼️ Preview Images")
    st.markdown("Generate and preview split-screen comparison images")

    # Check if script exists
    if not check_script():
        return

    # Display script info
    script_data = st.session_state.script_json or st.session_state.current_script
    metadata = script_data.get('metadata', {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Topic", metadata.get('topic', 'N/A')[:30] + "...")
    with col2:
        st.metric("Slides", len(script_data.get('slides', [])))
    with col3:
        st.metric("Language", metadata.get('language', 'vi').upper())
    with col4:
        if st.session_state.generated_images:
            st.metric("Images", len(st.session_state.generated_images))

    st.markdown("---")

    # Generation Controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        generate_btn = st.button(
            "🎨 Generate Images",
            type="primary",
            use_container_width=True,
            disabled=not script_data.get('slides')
        )

    with col2:
        if st.session_state.generated_images:
            if st.button("🔄 Regenerate All", use_container_width=True):
                st.session_state.generated_images = []
                st.rerun()

    with col3:
        if st.session_state.generated_images:
            # Create ZIP for download
            zip_path = create_zip_download(st.session_state.generated_images)
            if Path(zip_path).exists():
                with open(zip_path, 'rb') as f:
                    st.download_button(
                        "📦 Download All (ZIP)",
                        data=f.read(),
                        file_name=Path(zip_path).name,
                        mime="application/zip",
                        use_container_width=True
                    )

    with col4:
        if st.session_state.generated_images:
            if st.button("➡️ Create Video", type="primary", use_container_width=True):
                st.switch_page("pages/3_Create_Video.py")

    # Generate Images
    if generate_btn:
        with st.spinner("🎨 Generating images..."):
            if generate_images():
                st.success("✅ All images generated successfully!")
                st.balloons()
                st.rerun()

    # Display Gallery
    if st.session_state.generated_images:
        st.markdown("---")
        st.subheader("📸 Image Gallery")

        # Gallery options
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📊 {len(st.session_state.generated_images)} images generated")
        with col2:
            view_mode = st.selectbox("View Mode", ["Grid", "Carousel"])

        if view_mode == "Grid":
            display_image_gallery(st.session_state.generated_images)
        else:
            # Carousel view
            selected_idx = st.select_slider(
                "Select Image",
                options=list(range(len(st.session_state.generated_images))),
                format_func=lambda x: f"Slide {x + 1}"
            )

            if selected_idx < len(st.session_state.generated_images):
                img_path = st.session_state.generated_images[selected_idx]
                if Path(img_path).exists():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        image = Image.open(img_path)
                        st.image(image, caption=f"Slide {selected_idx + 1}", use_column_width=True)

                        # Download button for single image
                        with open(img_path, 'rb') as f:
                            st.download_button(
                                f"💾 Download Slide {selected_idx + 1}",
                                data=f.read(),
                                file_name=Path(img_path).name,
                                mime="image/png",
                                use_container_width=True
                            )

    # Instructions
    with st.expander("ℹ️ How to use this page"):
        st.markdown("""
        1. **Generate Images**: Click "Generate Images" to create split-screen images from your script
        2. **Preview**: Review each generated image in the gallery
        3. **Download**: Download individual images or all as a ZIP file
        4. **Regenerate**: If needed, regenerate all images with the button
        5. **Proceed**: Click "Create Video" to assemble images into a video

        **Image Specifications:**
        - Resolution: 1080x1920 (TikTok format)
        - Layout: Split-screen (Wrong vs Right)
        - Format: PNG with high quality
        - Style: Clean, minimalist design
        """)

if __name__ == "__main__":
    main()
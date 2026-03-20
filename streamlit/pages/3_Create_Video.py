"""Page for creating videos from images."""

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
    validate_video_duration
)
from components import (
    render_video_player,
    create_download_button,
    display_video_info,
    ProgressTracker
)

# Configure logging
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Create Video - TikTok Generator",
    page_icon="🎥",
    layout="wide"
)

def create_video_page():
    """Video creation and export page."""
    init_session_state()

    st.header("🎥 Create Video")
    st.markdown("Assemble your images into a TikTok-ready video")

    # Check prerequisites
    generated_images = get_state('generated_images', [])

    if not generated_images:
        # Try to find existing images
        output_dir = Path("output")
        if output_dir.exists():
            generated_images = get_file_list(str(output_dir), ['.png', '.jpg'])
            if generated_images:
                set_state('generated_images', generated_images)

    if not generated_images:
        st.warning("⚠️ Please generate images first in the 'Preview Images' page")
        return

    # Tab interface
    tab1, tab2, tab3 = st.tabs(["🎬 Create Video", "🎵 Music Settings", "📥 Export"])

    with tab1:
        create_video_interface(generated_images)

    with tab2:
        music_settings_interface()

    with tab3:
        export_interface()


def create_video_interface(images):
    """Interface for creating video from images."""
    st.subheader("Video Assembly")

    # Display source info
    st.info(f"📸 Using {len(images)} images for video creation")

    # Video settings
    col1, col2 = st.columns(2)

    config = get_state('config', {})

    with col1:
        duration_per_slide = st.slider(
            "Duration per slide (seconds)",
            min_value=2.0,
            max_value=5.0,
            value=config.get('duration_per_slide', 3.0),
            step=0.5,
            help="How long each slide appears"
        )

    with col2:
        transition_duration = st.slider(
            "Transition duration (seconds)",
            min_value=0.3,
            max_value=1.0,
            value=config.get('transition_duration', 0.5),
            step=0.1,
            help="Fade transition between slides"
        )

    # Calculate and validate total duration
    num_slides = len(images)
    is_valid, error_msg, total_duration = validate_video_duration(
        num_slides, duration_per_slide, transition_duration
    )

    if is_valid:
        st.success(f"✅ Total video duration: {total_duration:.1f} seconds")
    else:
        st.error(f"❌ {error_msg}")

    # Music selection
    st.divider()
    st.subheader("🎵 Background Music")

    music_option = st.radio(
        "Music Option",
        ["No music", "Use default music", "Upload custom music"],
        index=1
    )

    music_path = None
    if music_option == "Use default music":
        # Check for default music files
        audio_dir = Path("audio")
        if audio_dir.exists():
            music_files = get_file_list(str(audio_dir), ['.mp3', '.wav'])
            if music_files:
                music_path = st.selectbox(
                    "Select music file",
                    options=music_files,
                    format_func=lambda x: x.name
                )
            else:
                st.warning("No music files found in audio/ directory")

    elif music_option == "Upload custom music":
        uploaded_file = st.file_uploader(
            "Upload music file",
            type=['mp3', 'wav'],
            help="Upload your background music (MP3 or WAV)"
        )
        if uploaded_file:
            # Save uploaded file
            upload_dir = create_directory("audio/uploaded")
            music_path = upload_dir / uploaded_file.name
            with open(music_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Music uploaded: {uploaded_file.name}")

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)

        with col1:
            video_quality = st.selectbox(
                "Video Quality",
                ["High (1080p)", "Medium (720p)", "Low (480p)"],
                index=0
            )
            fps = st.selectbox("Frame Rate", [30, 60], index=0)

        with col2:
            video_codec = st.selectbox(
                "Video Codec",
                ["H.264 (Recommended)", "H.265"],
                index=0
            )
            audio_fade = st.checkbox("Fade audio in/out", value=True)

    # Create video button
    st.divider()
    if st.button("🚀 Create Video", type="primary", use_container_width=True):
        if not is_valid:
            st.error("Please adjust video settings to meet duration requirements")
            return

        create_video_from_images(
            images,
            duration_per_slide,
            transition_duration,
            music_path
        )


def create_video_from_images(images, duration_per_slide, transition_duration, music_path):
    """Create video from images using video_assembly module."""
    try:
        # Import video assembly module
        from video_assembly import VideoAssembler, VideoConfig

        # Create progress tracker
        total_steps = len(images) + 3
        progress = ProgressTracker(total_steps, "Creating Video")
        progress.update(1, "Initializing video encoder...")

        # Create video config
        config = VideoConfig(
            width=1080,
            height=1920,
            fps=30,
            timing={
                'duration_per_slide': duration_per_slide,
                'transition_duration': transition_duration
            }
        )

        # Initialize assembler
        assembler = VideoAssembler(config)
        progress.update(2, "Processing images...")

        # Prepare output path
        videos_dir = create_directory("videos")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = videos_dir / f"tiktok_{timestamp}.mp4"

        # Create video
        progress.update(3, "Encoding video...")

        # Convert Path objects to strings for the assembler
        image_paths = [str(img) for img in images]

        result = assembler.create_video(
            images=image_paths,
            output_path=str(output_path),
            music_path=str(music_path) if music_path else None
        )

        # Update progress for each image processed
        for i in range(len(images)):
            progress.update(4 + i, f"Processing slide {i + 1} of {len(images)}...")

        progress.complete("Video created successfully!")

        # Store in session state
        set_state('video_path', output_path)
        set_state('generation_status', 'video_ready')

        # Show success message
        st.success(f"✅ Video created successfully!")
        st.balloons()

        # Display video
        st.subheader("Preview")
        render_video_player(output_path)

        # Display info
        display_video_info(output_path)

    except Exception as e:
        st.error(f"Failed to create video: {str(e)}")
        logger.error(f"Video creation failed: {e}")


def music_settings_interface():
    """Music library and settings interface."""
    st.subheader("🎵 Music Library")

    # Check audio directory
    audio_dir = Path("audio")
    if not audio_dir.exists():
        create_directory("audio")

    music_files = get_file_list(str(audio_dir), ['.mp3', '.wav'])

    if music_files:
        st.success(f"Found {len(music_files)} music files")

        # List music files
        for music_file in music_files:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.text(f"🎵 {music_file.name}")

            with col2:
                size_mb = music_file.stat().st_size / (1024 * 1024)
                st.caption(f"{size_mb:.1f}MB")

            with col3:
                # Audio preview
                with open(music_file, 'rb') as f:
                    st.audio(f.read(), format='audio/mp3')
    else:
        st.info("No music files found. Add MP3 or WAV files to the audio/ directory")

    # Upload new music
    st.divider()
    st.subheader("Upload New Music")

    uploaded_file = st.file_uploader(
        "Choose music file",
        type=['mp3', 'wav'],
        help="Upload background music for your videos"
    )

    if uploaded_file:
        save_path = audio_dir / uploaded_file.name

        # Check if file exists
        if save_path.exists():
            st.warning(f"File {uploaded_file.name} already exists")
        else:
            # Save file
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.rerun()


def export_interface():
    """Video export and download interface."""
    st.subheader("📥 Export Video")

    video_path = get_state('video_path')

    if not video_path:
        # Check for existing videos
        videos_dir = Path("videos")
        if videos_dir.exists():
            video_files = get_file_list(str(videos_dir), ['.mp4', '.avi', '.mov'])
            if video_files:
                video_path = video_files[-1]  # Most recent
                set_state('video_path', video_path)

    if not video_path or not video_path.exists():
        st.info("No video available. Create a video in the 'Create Video' tab first.")
        return

    # Video preview
    st.subheader("Final Video")
    render_video_player(video_path)

    # Video info
    display_video_info(video_path)

    # Download options
    st.divider()
    st.subheader("Download Options")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📱 For TikTok")
        create_download_button(
            video_path,
            label="⬇️ Download MP4 for TikTok",
            mime_type="video/mp4"
        )
        st.caption("Optimized for TikTok upload")

    with col2:
        st.markdown("### 💾 Original File")
        create_download_button(
            video_path,
            label="⬇️ Download Original",
            mime_type="video/mp4"
        )
        st.caption("Full quality video file")

    # Export complete
    st.divider()
    st.success("🎉 Your TikTok video is ready!")
    st.info("""
    **Next Steps:**
    1. Download the video file
    2. Open TikTok app
    3. Tap '+' to create new post
    4. Upload your video
    5. Add captions, hashtags, and effects
    6. Post and share!
    """)

    # Reset workflow
    if st.button("🔄 Start New Project"):
        # Clear session state for new project
        from utils import clear_state
        clear_state(preserve_keys=['api_key', 'config'])
        st.success("Ready for new project!")
        st.rerun()


if __name__ == "__main__":
    create_video_page()
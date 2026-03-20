"""
Page 3: Create Video
Assemble images into a TikTok video with music and transitions
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from video_assembly import VideoAssembler, VideoConfig
except ImportError as e:
    st.error(f"Failed to import video_assembly: {e}")
    st.stop()

st.set_page_config(
    page_title="Create Video",
    page_icon="🎥",
    layout="wide"
)

def check_images():
    """Check if images exist in session state"""
    if not st.session_state.get('generated_images'):
        st.warning("⚠️ No images found. Please generate images first.")
        if st.button("← Go to Preview Images"):
            st.switch_page("pages/2_Preview_Images.py")
        return False

    # Verify images still exist
    valid_images = [p for p in st.session_state.generated_images if Path(p).exists()]
    if not valid_images:
        st.error("❌ Generated images not found. Please regenerate them.")
        if st.button("← Go to Preview Images"):
            st.switch_page("pages/2_Preview_Images.py")
        return False

    st.session_state.generated_images = valid_images
    return True

def get_available_music():
    """Get list of available music files"""
    audio_dir = Path('audio')
    music_files = []

    if audio_dir.exists():
        for ext in ['*.mp3', '*.wav', '*.m4a']:
            music_files.extend(audio_dir.glob(ext))

    return [str(f) for f in music_files]

def create_video(music_path=None):
    """Create video from images using video_assembly module"""
    try:
        st.session_state.generation_status = 'creating_video'

        # Initialize assembler
        assembler = VideoAssembler()

        # Create video config
        config = VideoConfig(
            images=st.session_state.generated_images,
            output_path=None,  # Will be auto-generated
            duration_per_image=st.session_state.config['duration_per_slide'],
            transition_duration=st.session_state.config['transition_duration'],
            music_path=music_path,
            resolution=(1080, 1920),
            fps=30
        )

        # Create video
        result = assembler.create_video(config)

        if result and result.success:
            st.session_state.video_path = result.output_path
            st.session_state.generation_status = 'completed'
            return True
        else:
            error_msg = result.error if result else "Unknown error"
            raise Exception(error_msg)

    except Exception as e:
        st.session_state.generation_status = 'error'
        st.session_state.error_log.append(str(e))
        st.error(f"❌ Video creation failed: {e}")
        return False

def display_video_player(video_path):
    """Display video player with controls"""
    if not Path(video_path).exists():
        st.error("Video file not found")
        return

    # Get file size
    file_size = Path(video_path).stat().st_size / (1024 * 1024)  # MB

    # Display video
    with open(video_path, 'rb') as video_file:
        video_bytes = video_file.read()
        st.video(video_bytes)

    # Video info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Size", f"{file_size:.2f} MB")
    with col2:
        st.metric("Format", "MP4")
    with col3:
        st.metric("Resolution", "1080x1920")

def main():
    st.title("🎥 Create Video")
    st.markdown("Assemble your images into a TikTok-ready video")

    # Check if images exist
    if not check_images():
        return

    # Display current status
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Images", len(st.session_state.generated_images))
    with col2:
        st.metric("Duration/Slide", f"{st.session_state.config['duration_per_slide']}s")
    with col3:
        st.metric("Transition", f"{st.session_state.config['transition_duration']}s")
    with col4:
        total_duration = (
            len(st.session_state.generated_images) * st.session_state.config['duration_per_slide'] -
            (len(st.session_state.generated_images) - 1) * st.session_state.config['transition_duration']
        )
        st.metric("Total Duration", f"~{total_duration:.1f}s")

    st.markdown("---")

    # Video Configuration
    st.subheader("⚙️ Video Configuration")

    col1, col2 = st.columns(2)

    with col1:
        # Duration settings
        st.session_state.config['duration_per_slide'] = st.slider(
            "Duration per Slide (seconds)",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.config['duration_per_slide'],
            step=0.5,
            help="How long each image should be displayed"
        )

        st.session_state.config['transition_duration'] = st.slider(
            "Transition Duration (seconds)",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.config['transition_duration'],
            step=0.1,
            help="Duration of fade transition between images"
        )

    with col2:
        # Music selection
        st.markdown("### 🎵 Background Music")

        music_option = st.radio(
            "Music Option",
            ["No Music", "Select from Library", "Upload Custom"]
        )

        music_path = None

        if music_option == "Select from Library":
            available_music = get_available_music()
            if available_music:
                selected_music = st.selectbox(
                    "Select Music",
                    options=["None"] + available_music,
                    format_func=lambda x: "No Music" if x == "None" else Path(x).name
                )
                if selected_music != "None":
                    music_path = selected_music
            else:
                st.info("No music files found in audio directory")

        elif music_option == "Upload Custom":
            uploaded_file = st.file_uploader(
                "Upload Music File",
                type=['mp3', 'wav', 'm4a'],
                help="Upload a music file for background audio"
            )

            if uploaded_file:
                # Save uploaded file
                upload_dir = Path('audio') / 'uploads'
                upload_dir.mkdir(parents=True, exist_ok=True)
                music_path = upload_dir / uploaded_file.name

                with open(music_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"✅ Uploaded: {uploaded_file.name}")

    st.markdown("---")

    # Generation Controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_btn = st.button(
            "🎬 Create Video",
            type="primary",
            use_container_width=True
        )

    with col2:
        if st.session_state.video_path and Path(st.session_state.video_path).exists():
            if st.button("🔄 Recreate", use_container_width=True):
                st.session_state.video_path = None
                st.rerun()

    with col3:
        if st.button("← Back to Images", use_container_width=True):
            st.switch_page("pages/2_Preview_Images.py")

    with col4:
        if st.session_state.video_path and Path(st.session_state.video_path).exists():
            with open(st.session_state.video_path, 'rb') as f:
                st.download_button(
                    "⬇️ Download Video",
                    data=f.read(),
                    file_name=f"tiktok_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )

    # Create Video
    if create_btn:
        with st.spinner("🎬 Creating video... This may take a few moments"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Update progress
            status_text.text("Initializing video assembly...")
            progress_bar.progress(20)

            status_text.text("Processing images...")
            progress_bar.progress(40)

            status_text.text("Adding transitions...")
            progress_bar.progress(60)

            if music_path:
                status_text.text("Adding background music...")
                progress_bar.progress(80)

            # Create the video
            if create_video(music_path):
                progress_bar.progress(100)
                status_text.text("Video created successfully!")
                st.success("✅ Video created successfully!")
                st.balloons()
                st.rerun()
            else:
                progress_bar.progress(0)
                status_text.text("Video creation failed")

    # Display Video
    if st.session_state.video_path and Path(st.session_state.video_path).exists():
        st.markdown("---")
        st.subheader("🎞️ Preview Video")

        display_video_player(st.session_state.video_path)

        # Success message
        st.success("""
        🎉 **Your TikTok video is ready!**

        You can now download the video and upload it to TikTok.
        The video is optimized for TikTok's format (1080x1920) and includes
        smooth transitions between slides.
        """)

        # Share instructions
        with st.expander("📱 How to upload to TikTok"):
            st.markdown("""
            1. **Download the video** using the button above
            2. **Open TikTok** app on your phone
            3. **Tap the + button** to create a new post
            4. **Select "Upload"** and choose your video
            5. **Add caption and hashtags**:
               - Use relevant parenting hashtags (#parenting #khoibennoi)
               - Add trending sounds if desired
            6. **Post** and watch the engagement grow!

            **Recommended Hashtags:**
            - Vietnamese: #nuoicon #lamme #khoibennoi #mecondangiu
            - English: #parenting #parentingtips #momlife #parenthack
            """)

    # Instructions
    with st.expander("ℹ️ How to use this page"):
        st.markdown("""
        1. **Configure Settings**: Adjust slide duration and transition time
        2. **Add Music** (Optional): Select from library or upload your own
        3. **Create Video**: Click the button to assemble your video
        4. **Preview**: Watch the generated video
        5. **Download**: Save the video to your device
        6. **Upload**: Share on TikTok!

        **Video Specifications:**
        - Format: MP4 (H.264)
        - Resolution: 1080x1920 (9:16 aspect ratio)
        - FPS: 30 frames per second
        - Transitions: Smooth fade effects
        - Audio: Optional background music
        """)

if __name__ == "__main__":
    main()
"""
TikTok Content Generator - Streamlit Dashboard
Main application entry point
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="TikTok Content Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF0050 0%, #FF4081 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .workflow-step {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #f0f0f0;
        margin: 0.5rem 0;
    }
    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        background: #FF0050;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.api_key = os.getenv('OPENAI_API_KEY', '')
        st.session_state.current_script = None
        st.session_state.script_json = None
        st.session_state.generated_images = []
        st.session_state.video_path = None
        st.session_state.generation_status = 'idle'
        st.session_state.error_log = []
        st.session_state.config = {
            'num_slides': 5,
            'language': 'vi',
            'duration_per_slide': 3.0,
            'transition_duration': 0.5,
            'music_path': None
        }

def sidebar_config():
    """Configure sidebar with API key and settings"""
    with st.sidebar:
        st.title("⚙️ Configuration")

        # API Key Configuration
        st.subheader("🔑 API Key")
        api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_key,
            type="password",
            help="Enter your OpenAI API key (sk-...)"
        )

        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key

        if api_key and api_key.startswith('sk-'):
            st.success("✅ API Key configured")
        elif api_key:
            st.error("❌ Invalid API key format")
        else:
            st.warning("⚠️ API key required for content generation")

        # Generation Settings
        st.subheader("📝 Generation Settings")

        st.session_state.config['num_slides'] = st.slider(
            "Number of Slides",
            min_value=3,
            max_value=10,
            value=st.session_state.config['num_slides'],
            help="Number of comparison slides to generate"
        )

        st.session_state.config['language'] = st.selectbox(
            "Language",
            options=['vi', 'en'],
            index=0 if st.session_state.config['language'] == 'vi' else 1,
            format_func=lambda x: "🇻🇳 Tiếng Việt" if x == 'vi' else "🇬🇧 English"
        )

        # Video Settings
        st.subheader("🎥 Video Settings")

        st.session_state.config['duration_per_slide'] = st.slider(
            "Duration per Slide (seconds)",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.config['duration_per_slide'],
            step=0.5
        )

        st.session_state.config['transition_duration'] = st.slider(
            "Transition Duration (seconds)",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.config['transition_duration'],
            step=0.1
        )

        # Status Display
        st.subheader("📊 Current Status")
        status_color = {
            'idle': '⚪',
            'generating_script': '🟡',
            'generating_images': '🟠',
            'creating_video': '🔵',
            'completed': '🟢',
            'error': '🔴'
        }

        status = st.session_state.generation_status
        st.write(f"{status_color.get(status, '⚪')} {status.replace('_', ' ').title()}")

        # Session Info
        if st.session_state.current_script:
            st.success("✅ Script generated")
        if st.session_state.generated_images:
            st.success(f"✅ {len(st.session_state.generated_images)} images created")
        if st.session_state.video_path:
            st.success("✅ Video ready for download")

def main_content():
    """Display main content and workflow"""
    # Header
    st.markdown('<h1 class="main-header">🎬 TikTok Content Generator</h1>', unsafe_allow_html=True)
    st.markdown("### Transform parenting topics into engaging TikTok content")

    # Introduction
    st.info("""
    **Welcome to the TikTok Content Generator Dashboard!**

    This tool helps you create professional TikTok videos about parenting topics using AI.
    Follow the simple 3-step workflow below to generate your content.
    """)

    # Workflow Overview
    st.subheader("📋 Workflow Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="workflow-step">
            <span class="step-number">1</span>
            <strong>Generate Script</strong><br>
            Enter a parenting topic and let AI create a "Wrong vs Right" comparison script
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="workflow-step">
            <span class="step-number">2</span>
            <strong>Preview Images</strong><br>
            Review and customize the generated split-screen images
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="workflow-step">
            <span class="step-number">3</span>
            <strong>Create Video</strong><br>
            Assemble images into a video with music and transitions
        </div>
        """, unsafe_allow_html=True)

    # Quick Start Guide
    st.subheader("🚀 Quick Start")

    tab1, tab2, tab3 = st.tabs(["Getting Started", "Features", "Tips"])

    with tab1:
        st.markdown("""
        1. **Configure your API key** in the sidebar (required for AI generation)
        2. **Navigate to "1_Generate_Script"** page using the sidebar menu
        3. **Enter a parenting topic** and generate your script
        4. **Preview and edit** the generated content
        5. **Create images** from your script
        6. **Assemble the final video** with music
        7. **Download** your TikTok-ready content!
        """)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **✨ Key Features:**
            - AI-powered script generation
            - Customizable Vietnamese/English content
            - Split-screen "Sai vs Đúng" layout
            - Automatic image generation
            - Video assembly with transitions
            - Background music support
            """)

        with col2:
            st.markdown("""
            **🛠️ Technical Capabilities:**
            - OpenAI GPT-4 integration
            - High-quality 1080x1920 images
            - FFmpeg video processing
            - Session state persistence
            - Error recovery mechanisms
            - Real-time progress tracking
            """)

    with tab3:
        st.markdown("""
        **💡 Pro Tips:**
        - Use specific, detailed topics for better results
        - Keep topics focused on single parenting concepts
        - Review and edit scripts before generating images
        - Test with 3-5 slides first before creating longer videos
        - Save your API key in the `.env` file for persistence
        """)

    # Current Session Summary
    if any([st.session_state.current_script,
            st.session_state.generated_images,
            st.session_state.video_path]):

        st.subheader("📈 Current Session Progress")

        progress_cols = st.columns(3)

        with progress_cols[0]:
            if st.session_state.current_script:
                st.metric("Script", "✅ Ready",
                         f"{len(st.session_state.current_script.get('slides', []))} slides")
            else:
                st.metric("Script", "⏳ Not started", "")

        with progress_cols[1]:
            if st.session_state.generated_images:
                st.metric("Images", "✅ Generated",
                         f"{len(st.session_state.generated_images)} images")
            else:
                st.metric("Images", "⏳ Not started", "")

        with progress_cols[2]:
            if st.session_state.video_path:
                st.metric("Video", "✅ Complete", "Ready to download")
            else:
                st.metric("Video", "⏳ Not started", "")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        Made with ❤️ for Khôi Bên Nôi | Powered by OpenAI & Streamlit
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    initialize_session_state()
    sidebar_config()
    main_content()

if __name__ == "__main__":
    main()
import streamlit as st
import sys
from pathlib import Path
import json
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import utilities
from utils import (
    init_session_state,
    get_state,
    set_state,
    update_config,
    validate_api_key,
    validate_topic,
    create_directory,
    get_latest_state_file,
    load_state_from_disk
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        font-size: 3rem;
        color: #FF0050;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .stButton > button {
        background-color: #FF0050;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #E6004A;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    init_session_state()

    # Check for recovery option
    if not get_state('initialized', False):
        latest_state = get_latest_state_file()
        if latest_state:
            if st.info("Found previous session. Would you like to restore it?"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Restore Session"):
                        if load_state_from_disk(latest_state):
                            st.success("Session restored!")
                            st.rerun()
                with col2:
                    if st.button("🆕 Start Fresh"):
                        set_state('initialized', True)
                        st.rerun()
        else:
            set_state('initialized', True)

    # Header
    st.markdown('<h1 class="main-header">🎬 TikTok Content Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Tự động tạo nội dung TikTok về kiến thức nuôi con</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Cấu hình")

        # API Configuration
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=get_state('api_key', ''),
            help="Nhập API key của bạn"
        )

        if api_key:
            is_valid, error_msg = validate_api_key(api_key)
            if is_valid:
                set_state('api_key', api_key)
                st.success("✅ API Key đã được cấu hình")
            else:
                st.error(f"❌ {error_msg}")

        st.divider()

        # Generation settings
        st.subheader("📝 Thiết lập sinh nội dung")
        config = get_state('config', {})

        num_slides = st.slider(
            "Số lượng slide",
            min_value=3,
            max_value=10,
            value=config.get('num_slides', 5)
        )
        language = st.selectbox(
            "Ngôn ngữ",
            ["vi", "en"],
            index=0 if config.get('language', 'vi') == 'vi' else 1
        )

        # Update config in session state
        update_config({'num_slides': num_slides, 'language': language})

        st.divider()

        # Video settings
        st.subheader("🎥 Thiết lập video")
        duration_per_slide = st.slider(
            "Thời gian mỗi slide (giây)",
            min_value=2,
            max_value=5,
            value=config.get('duration_per_slide', 3)
        )
        transition_duration = st.slider(
            "Thời gian chuyển cảnh (giây)",
            min_value=0.3,
            max_value=1.0,
            value=config.get('transition_duration', 0.5),
            step=0.1
        )

        # Update config
        update_config({
            'duration_per_slide': float(duration_per_slide),
            'transition_duration': float(transition_duration)
        })

        st.divider()

        # Session info
        st.subheader("📊 Session Info")
        if get_state('current_script'):
            st.success("✅ Script generated")
        if get_state('generated_images'):
            st.success(f"✅ {len(get_state('generated_images', []))} images created")
        if get_state('video_path'):
            st.success("✅ Video ready")

    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Quick Start section
        st.header("🚀 Bắt đầu nhanh")

        # Topic input
        topic = st.text_area(
            "Nhập chủ đề về nuôi con",
            placeholder="Ví dụ: Cách dạy con không la mắng, Phương pháp dạy con tự lập...",
            height=100
        )

        if st.button("🎯 Tạo kịch bản", use_container_width=True):
            # Validate inputs
            api_key = get_state('api_key', '')

            if not api_key:
                st.error("⚠️ Vui lòng nhập OpenAI API Key trong phần cấu hình!")
            else:
                is_valid, error_msg = validate_topic(topic)
                if not is_valid:
                    st.error(f"⚠️ {error_msg}")
                else:
                with st.spinner("Đang tạo kịch bản..."):
                    try:
                        # Import content generator
                        from content_generator import ScriptGenerator

                        # Generate script
                        generator = ScriptGenerator(api_key=api_key)
                        script = generator.generate(
                            topic=topic,
                            num_slides=num_slides,
                            language=language
                        )

                        # Store in session state
                        set_state('current_script', script)
                        set_state('script_json', script.model_dump())
                        set_state('generation_status', 'script_ready')
                        st.success("✅ Kịch bản đã được tạo thành công!")

                        # Display script preview
                        st.subheader("📋 Xem trước kịch bản")
                        st.json(script.model_dump())

                        # Navigation hint
                        st.info("💡 Chuyển sang trang '1_Generate_Script' để xem chi tiết và chỉnh sửa")

                    except Exception as e:
                        logger.error(f"Error generating script: {e}")
                        st.error(f"❌ Lỗi: {str(e)}")

    # Features showcase
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📝 Tạo kịch bản
        - AI tự động sinh nội dung
        - Format "Sai vs Đúng"
        - Tiếng Việt tối ưu
        """)

    with col2:
        st.markdown("""
        ### 🎨 Thiết kế hình ảnh
        - Layout chia đôi màn hình
        - Tự động chèn text & icon
        - Xuất ảnh 1080x1920
        """)

    with col3:
        st.markdown("""
        ### 🎥 Ghép video
        - Tự động tạo slideshow
        - Thêm nhạc nền
        - Xuất MP4 cho TikTok
        """)

    # Instructions
    with st.expander("📖 Hướng dẫn sử dụng"):
        st.markdown("""
        1. **Cấu hình API Key**: Nhập OpenAI API key trong sidebar
        2. **Nhập chủ đề**: Điền chủ đề về nuôi con bạn muốn tạo nội dung
        3. **Tạo kịch bản**: Click nút để AI sinh kịch bản
        4. **Xem trước & chỉnh sửa**: Kiểm tra kịch bản được tạo
        5. **Tạo hình ảnh**: Vào trang "Preview Images" để render ảnh
        6. **Xuất video**: Vào trang "Create Video" để ghép video final

        **Lưu ý**: Cần có FFmpeg được cài đặt để tạo video.
        """)

    # Workflow Status
    st.divider()
    st.subheader("📈 Workflow Progress")

    # Create workflow steps indicator
    steps = ["Topic Input", "Script Generation", "Image Creation", "Video Assembly"]
    status = get_state('generation_status', 'idle')

    current_step = 0
    if status == 'script_ready':
        current_step = 1
    elif status == 'images_ready':
        current_step = 2
    elif status == 'video_ready':
        current_step = 3

    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i <= current_step:
                st.success(f"✅ {step}")
            else:
                st.info(f"⭕ {step}")

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #999;'>
        <small>Powered by OpenAI GPT-4 | Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
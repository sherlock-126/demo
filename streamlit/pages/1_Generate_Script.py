"""
Page 1: Generate Script
Generate AI-powered content scripts from parenting topics
"""

import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from content_generator import ScriptGenerator, ScriptModel
except ImportError as e:
    st.error(f"Failed to import content_generator: {e}")
    st.stop()

st.set_page_config(
    page_title="Generate Script",
    page_icon="📝",
    layout="wide"
)

def validate_api_key():
    """Validate API key is configured"""
    if not st.session_state.get('api_key'):
        st.error("❌ Please configure your OpenAI API key in the sidebar first")
        return False
    if not st.session_state.api_key.startswith('sk-'):
        st.error("❌ Invalid API key format. Should start with 'sk-'")
        return False
    return True

def generate_script(topic: str):
    """Generate script using content_generator module"""
    try:
        # Update status
        st.session_state.generation_status = 'generating_script'

        # Initialize generator
        generator = ScriptGenerator(api_key=st.session_state.api_key)

        # Generate script
        script = generator.generate(
            topic=topic,
            num_slides=st.session_state.config['num_slides'],
            language=st.session_state.config['language']
        )

        # Convert to dict if it's a model
        if hasattr(script, 'dict'):
            script_dict = script.dict()
        else:
            script_dict = script

        # Store in session state
        st.session_state.current_script = script
        st.session_state.script_json = script_dict

        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path('data') / f'script_{timestamp}.json'
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(script_dict, f, ensure_ascii=False, indent=2)

        st.session_state.generation_status = 'script_complete'
        return True

    except Exception as e:
        st.session_state.generation_status = 'error'
        st.session_state.error_log.append(str(e))
        st.error(f"❌ Script generation failed: {e}")
        return False

def display_script(script_data):
    """Display generated script in a formatted way"""
    if not script_data:
        return

    # Script metadata
    metadata = script_data.get('metadata', {})
    if metadata:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Topic", metadata.get('topic', 'N/A'))
        with col2:
            st.metric("Language", metadata.get('language', 'vi').upper())
        with col3:
            st.metric("Slides", len(script_data.get('slides', [])))

    # Display slides
    slides = script_data.get('slides', [])
    for idx, slide in enumerate(slides, 1):
        with st.expander(f"Slide {idx}: {slide.get('title', 'Untitled')}", expanded=(idx == 1)):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ❌ Sai (Wrong)")
                wrong = slide.get('wrong', {})
                st.write(f"**Text:** {wrong.get('text', '')}")
                st.write(f"**Description:** {wrong.get('description', '')}")

            with col2:
                st.markdown("### ✅ Đúng (Right)")
                right = slide.get('right', {})
                st.write(f"**Text:** {right.get('text', '')}")
                st.write(f"**Description:** {right.get('description', '')}")

            if slide.get('subtitle'):
                st.info(f"**Subtitle:** {slide.get('subtitle')}")

def main():
    st.title("📝 Generate Script")
    st.markdown("Generate AI-powered comparison scripts for TikTok content")

    # Check if API key is configured
    if not validate_api_key():
        st.info("👈 Please configure your API key in the sidebar to continue")
        return

    # Topic Input Section
    st.subheader("🎯 Enter Your Topic")

    col1, col2 = st.columns([3, 1])

    with col1:
        topic = st.text_area(
            "Parenting Topic",
            placeholder="E.g., Cách dạy con tự lập từ nhỏ, How to handle toddler tantrums, etc.",
            height=100,
            help="Enter a specific parenting topic. The AI will generate a 'Wrong vs Right' comparison script."
        )

    with col2:
        st.markdown("### Quick Examples:")
        if st.button("🍼 Cho con ăn dặm"):
            topic = "Cách cho con ăn dặm đúng cách và an toàn"
        if st.button("😴 Dạy con ngủ"):
            topic = "Phương pháp dạy con tự ngủ không khóc"
        if st.button("📚 Dạy con đọc"):
            topic = "Cách dạy con yêu thích đọc sách từ nhỏ"

    # Generation Controls
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        generate_btn = st.button(
            "🚀 Generate Script",
            type="primary",
            disabled=not topic or len(topic) < 10,
            use_container_width=True
        )

    with col2:
        if st.session_state.current_script:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.current_script = None
                st.session_state.script_json = None
                st.rerun()

    with col3:
        if topic and len(topic) < 10:
            st.warning("Topic should be at least 10 characters long")

    # Generate Script
    if generate_btn and topic:
        with st.spinner(f"🤖 Generating script with {st.session_state.config['num_slides']} slides..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Simulate progress updates
            status_text.text("Connecting to OpenAI...")
            progress_bar.progress(20)

            status_text.text("Analyzing topic...")
            progress_bar.progress(40)

            status_text.text("Generating comparison slides...")
            progress_bar.progress(60)

            # Generate the script
            if generate_script(topic):
                progress_bar.progress(100)
                status_text.text("Script generated successfully!")
                st.success("✅ Script generated successfully!")
                st.balloons()
            else:
                progress_bar.progress(0)
                status_text.text("Generation failed")

    # Display Generated Script
    if st.session_state.current_script:
        st.markdown("---")
        st.subheader("📄 Generated Script")

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📋 Copy JSON", use_container_width=True):
                st.code(json.dumps(st.session_state.script_json, ensure_ascii=False, indent=2))

        with col2:
            # Download JSON
            if st.session_state.script_json:
                json_str = json.dumps(st.session_state.script_json, ensure_ascii=False, indent=2)
                st.download_button(
                    "💾 Download JSON",
                    data=json_str,
                    file_name=f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col3:
            edit_mode = st.checkbox("✏️ Edit Mode")

        with col4:
            if st.button("➡️ Generate Images", type="primary", use_container_width=True):
                st.switch_page("pages/2_Preview_Images.py")

        # Display or Edit Script
        if edit_mode:
            st.info("📝 Edit the JSON below and click 'Save Changes' to update")
            edited_json = st.text_area(
                "Script JSON",
                value=json.dumps(st.session_state.script_json, ensure_ascii=False, indent=2),
                height=400
            )

            if st.button("💾 Save Changes"):
                try:
                    st.session_state.script_json = json.loads(edited_json)
                    st.session_state.current_script = st.session_state.script_json
                    st.success("✅ Changes saved!")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
        else:
            display_script(st.session_state.script_json)

    # Instructions
    with st.expander("ℹ️ How to use this page"):
        st.markdown("""
        1. **Enter a topic**: Type a specific parenting topic in Vietnamese or English
        2. **Configure settings**: Adjust the number of slides and language in the sidebar
        3. **Generate script**: Click the Generate button to create your content
        4. **Review**: Check each slide to ensure the content is accurate
        5. **Edit if needed**: Toggle edit mode to modify the script
        6. **Proceed**: Click "Generate Images" to move to the next step

        **Tips:**
        - Be specific with your topics for better results
        - Start with 3-5 slides for testing
        - Review the generated content before proceeding
        """)

if __name__ == "__main__":
    main()
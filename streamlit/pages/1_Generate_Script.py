"""Page for generating and editing scripts."""

import streamlit as st
import sys
from pathlib import Path
import json
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    init_session_state,
    get_state,
    set_state,
    validate_api_key,
    validate_topic
)
from components import display_script, edit_script_slide, ProgressTracker

# Configure logging
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Generate Script - TikTok Generator",
    page_icon="📝",
    layout="wide"
)

def generate_script_page():
    """Script generation and editing page."""
    init_session_state()

    st.header("📝 Generate Script")
    st.markdown("Create AI-powered content scripts for your TikTok videos")

    # Check API key
    api_key = get_state('api_key', '')
    if not api_key:
        st.warning("⚠️ Please configure your OpenAI API key in the main page sidebar")
        return

    # Tab interface
    tab1, tab2, tab3 = st.tabs(["✨ Generate New", "📋 View Current", "✏️ Edit Script"])

    with tab1:
        generate_new_script()

    with tab2:
        view_current_script()

    with tab3:
        edit_current_script()


def generate_new_script():
    """Generate new script interface."""
    st.subheader("Generate New Script")

    # Topic input
    col1, col2 = st.columns([3, 1])

    with col1:
        topic = st.text_area(
            "Enter your parenting topic",
            placeholder="Example: Teaching children independence, Positive discipline methods...",
            height=100,
            help="Describe the parenting topic you want to create content about"
        )

    with col2:
        st.markdown("### Options")
        config = get_state('config', {})

        num_slides = st.number_input(
            "Number of slides",
            min_value=3,
            max_value=10,
            value=config.get('num_slides', 5)
        )

        language = st.selectbox(
            "Language",
            options=["vi", "en"],
            index=0 if config.get('language', 'vi') == 'vi' else 1
        )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)

        with col1:
            tone = st.selectbox(
                "Content Tone",
                ["Educational", "Friendly", "Professional", "Casual"],
                index=0
            )

        with col2:
            include_advice = st.checkbox("Include advice section", value=True)

    # Generate button
    if st.button("🚀 Generate Script", type="primary", use_container_width=True):
        if not topic:
            st.error("Please enter a topic")
            return

        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            st.error(error_msg)
            return

        # Generate script
        with st.spinner("Generating script..."):
            try:
                from content_generator import ScriptGenerator

                # Create progress tracker
                progress = ProgressTracker(3, "Generating Script")
                progress.update(1, "Initializing AI model...")

                # Initialize generator
                generator = ScriptGenerator(api_key=get_state('api_key'))
                progress.update(2, "Creating content...")

                # Generate script
                script = generator.generate(
                    topic=topic,
                    num_slides=num_slides,
                    language=language
                )

                progress.update(3, "Finalizing script...")

                # Store in session state
                set_state('current_script', script)
                set_state('script_json', script.model_dump())
                set_state('generation_status', 'script_ready')

                progress.complete("Script generated successfully!")

                # Show preview
                st.success("✅ Script generated successfully!")
                with st.expander("Preview Script", expanded=True):
                    display_script(script.model_dump())

                # Next step hint
                st.info("💡 Go to 'Preview Images' page to generate visuals for your script")

            except Exception as e:
                st.error(f"Failed to generate script: {str(e)}")
                logger.error(f"Script generation failed: {e}")


def view_current_script():
    """View current script interface."""
    st.subheader("Current Script")

    script_json = get_state('script_json')

    if not script_json:
        st.info("No script available. Generate a new script in the 'Generate New' tab.")
        return

    # Display options
    col1, col2 = st.columns(2)

    with col1:
        show_json = st.checkbox("Show JSON view", value=False)

    with col2:
        if st.button("📥 Download Script"):
            # Download as JSON
            json_str = json.dumps(script_json, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    # Display script
    display_script(script_json, show_json=show_json)

    # Stats
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Slides", len(script_json.get('slides', [])))
    with col2:
        st.metric("Language", script_json.get('metadata', {}).get('language', 'vi').upper())
    with col3:
        st.metric("Status", "Ready for images" if get_state('generation_status') == 'script_ready' else "In progress")


def edit_current_script():
    """Edit current script interface."""
    st.subheader("Edit Script")

    script_json = get_state('script_json')

    if not script_json:
        st.info("No script available to edit. Generate a new script first.")
        return

    # Slide selector
    slides = script_json.get('slides', [])
    slide_options = [f"Slide {i+1}: {slide.get('title', 'Untitled')}" for i, slide in enumerate(slides)]

    selected_slide = st.selectbox(
        "Select slide to edit",
        options=range(len(slides)),
        format_func=lambda x: slide_options[x]
    )

    if selected_slide is not None:
        # Edit interface
        st.divider()
        updated_slide = edit_script_slide(selected_slide)

        if updated_slide:
            st.balloons()
            st.rerun()


if __name__ == "__main__":
    generate_script_page()
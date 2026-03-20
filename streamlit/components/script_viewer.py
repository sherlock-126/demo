"""Script viewer component for displaying and editing generated scripts."""

import streamlit as st
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def display_script(script_data: Dict[str, Any], show_json: bool = False) -> None:
    """Display script in formatted view.

    Args:
        script_data: Script dictionary containing slides
        show_json: Whether to show raw JSON view
    """
    if not script_data:
        st.warning("No script data to display")
        return

    # Display metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Slides", len(script_data.get('slides', [])))
    with col2:
        st.metric("Language", script_data.get('metadata', {}).get('language', 'vi').upper())
    with col3:
        st.metric("Theme", script_data.get('metadata', {}).get('theme', 'Parenting'))

    st.divider()

    # Toggle between views
    if show_json:
        st.json(script_data)
    else:
        # Display slides in formatted view
        slides = script_data.get('slides', [])
        for i, slide in enumerate(slides):
            with st.expander(f"Slide {i + 1}: {slide.get('title', 'Untitled')}", expanded=(i == 0)):
                _display_slide_content(slide)


def _display_slide_content(slide: Dict[str, Any]) -> None:
    """Display single slide content.

    Args:
        slide: Slide dictionary
    """
    # Title
    st.subheader(slide.get('title', 'Untitled'))

    # Content sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**❌ Sai (Wrong)**")
        wrong_content = slide.get('wrong', {})
        st.markdown(f"**Text:** {wrong_content.get('text', '')}")
        st.markdown(f"**Icon:** {wrong_content.get('icon', '❌')}")

    with col2:
        st.markdown("**✅ Đúng (Right)**")
        right_content = slide.get('right', {})
        st.markdown(f"**Text:** {right_content.get('text', '')}")
        st.markdown(f"**Icon:** {right_content.get('icon', '✅')}")

    # Advice
    if 'advice' in slide:
        st.info(f"💡 **Lời khuyên:** {slide['advice']}")


def edit_script_slide(slide_index: int) -> Optional[Dict[str, Any]]:
    """Edit a specific slide in the script.

    Args:
        slide_index: Index of slide to edit

    Returns:
        Updated slide dictionary or None if cancelled
    """
    if 'script_json' not in st.session_state or not st.session_state['script_json']:
        st.error("No script available to edit")
        return None

    slides = st.session_state['script_json'].get('slides', [])

    if slide_index >= len(slides):
        st.error(f"Invalid slide index: {slide_index}")
        return None

    slide = slides[slide_index].copy()

    st.subheader(f"Edit Slide {slide_index + 1}")

    # Edit title
    new_title = st.text_input("Title", value=slide.get('title', ''))

    # Edit wrong side
    st.markdown("### ❌ Wrong Side")
    wrong_text = st.text_area("Wrong Text", value=slide.get('wrong', {}).get('text', ''))
    wrong_icon = st.text_input("Wrong Icon", value=slide.get('wrong', {}).get('icon', '❌'))

    # Edit right side
    st.markdown("### ✅ Right Side")
    right_text = st.text_area("Right Text", value=slide.get('right', {}).get('text', ''))
    right_icon = st.text_input("Right Icon", value=slide.get('right', {}).get('icon', '✅'))

    # Edit advice
    advice = st.text_area("Advice", value=slide.get('advice', ''))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
            # Update slide
            updated_slide = {
                'title': new_title,
                'wrong': {
                    'text': wrong_text,
                    'icon': wrong_icon
                },
                'right': {
                    'text': right_text,
                    'icon': right_icon
                },
                'advice': advice
            }

            # Update session state
            slides[slide_index] = updated_slide
            st.session_state['script_json']['slides'] = slides
            st.success(f"Slide {slide_index + 1} updated!")
            return updated_slide

    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            return None

    return None


def get_script_summary(script_data: Dict[str, Any]) -> str:
    """Generate a summary of the script.

    Args:
        script_data: Script dictionary

    Returns:
        Summary string
    """
    if not script_data:
        return "No script available"

    slides = script_data.get('slides', [])
    metadata = script_data.get('metadata', {})

    summary = f"""
    **Script Summary:**
    - Total Slides: {len(slides)}
    - Language: {metadata.get('language', 'vi').upper()}
    - Topic: {metadata.get('topic', 'N/A')}
    - Generated: {metadata.get('generated_at', 'N/A')}
    """

    return summary
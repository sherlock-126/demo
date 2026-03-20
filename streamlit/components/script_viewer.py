"""
Script viewer component for displaying and editing scripts
"""

import streamlit as st
import json


def display_script(script_data, expanded=False):
    """Display script in formatted view"""
    if not script_data:
        st.warning("No script data available")
        return

    slides = script_data.get('slides', [])

    for idx, slide in enumerate(slides, 1):
        with st.expander(f"Slide {idx}: {slide.get('title', 'Untitled')}", expanded=expanded):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ❌ Wrong")
                wrong = slide.get('wrong', {})
                st.write(f"**Text:** {wrong.get('text', '')}")
                st.write(f"**Description:** {wrong.get('description', '')}")

            with col2:
                st.markdown("### ✅ Right")
                right = slide.get('right', {})
                st.write(f"**Text:** {right.get('text', '')}")
                st.write(f"**Description:** {right.get('description', '')}")

            if slide.get('subtitle'):
                st.info(f"**Subtitle:** {slide.get('subtitle')}")


def edit_script(script_data):
    """Edit script in JSON format"""
    if not script_data:
        st.warning("No script to edit")
        return None

    json_str = json.dumps(script_data, ensure_ascii=False, indent=2)

    edited = st.text_area(
        "Edit Script JSON",
        value=json_str,
        height=400,
        help="Edit the JSON and click Save to update"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes", type="primary"):
            try:
                updated_script = json.loads(edited)
                st.success("✅ Script updated successfully")
                return updated_script
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")

    with col2:
        if st.button("🔄 Reset"):
            st.rerun()

    return None
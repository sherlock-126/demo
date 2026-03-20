"""
Progress tracking component for long-running operations
"""

import streamlit as st
import time


def show_progress(total_steps, current_step=0):
    """Show progress bar with status"""
    progress = st.progress(current_step / total_steps if total_steps > 0 else 0)
    status_text = st.empty()

    return progress, status_text


def update_status(progress, status_text, current_step, total_steps, message=""):
    """Update progress bar and status message"""
    if progress and current_step <= total_steps:
        progress.progress(current_step / total_steps if total_steps > 0 else 0)

    if status_text and message:
        status_text.text(message)

    return current_step + 1
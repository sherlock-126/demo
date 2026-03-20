"""
Session state management utilities
"""

import streamlit as st
import pickle
from pathlib import Path


def init_session_state(defaults=None):
    """Initialize session state with defaults"""
    if defaults is None:
        defaults = {
            'initialized': True,
            'api_key': '',
            'current_script': None,
            'script_json': None,
            'generated_images': [],
            'video_path': None,
            'generation_status': 'idle',
            'error_log': [],
            'config': {
                'num_slides': 5,
                'language': 'vi',
                'duration_per_slide': 3.0,
                'transition_duration': 0.5,
                'music_path': None
            }
        }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_state(filename="session_state.pkl"):
    """Save session state to file"""
    state_file = Path("data") / filename
    state_file.parent.mkdir(exist_ok=True)

    state_dict = dict(st.session_state)

    with open(state_file, 'wb') as f:
        pickle.dump(state_dict, f)

    return str(state_file)


def load_state(filename="session_state.pkl"):
    """Load session state from file"""
    state_file = Path("data") / filename

    if not state_file.exists():
        return False

    try:
        with open(state_file, 'rb') as f:
            state_dict = pickle.load(f)

        for key, value in state_dict.items():
            st.session_state[key] = value

        return True

    except Exception:
        return False
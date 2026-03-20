"""Session state management utilities for Streamlit."""

import streamlit as st
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def init_session_state() -> None:
    """Initialize session state with default values."""
    defaults = {
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
        },
        'session_id': datetime.now().strftime('%Y%m%d_%H%M%S')
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_state(key: str, default: Any = None) -> Any:
    """Get value from session state.

    Args:
        key: State key
        default: Default value if key doesn't exist

    Returns:
        State value or default
    """
    return st.session_state.get(key, default)


def set_state(key: str, value: Any) -> None:
    """Set value in session state.

    Args:
        key: State key
        value: Value to store
    """
    st.session_state[key] = value
    logger.debug(f"State updated: {key}")


def update_config(config_dict: Dict[str, Any]) -> None:
    """Update configuration in session state.

    Args:
        config_dict: Dictionary of configuration values
    """
    if 'config' not in st.session_state:
        st.session_state['config'] = {}

    st.session_state['config'].update(config_dict)
    logger.debug(f"Config updated: {config_dict.keys()}")


def clear_state(preserve_keys: List[str] = None) -> None:
    """Clear session state, optionally preserving certain keys.

    Args:
        preserve_keys: List of keys to preserve during clear
    """
    preserve_keys = preserve_keys or ['api_key', 'config']
    preserved = {}

    # Save preserved keys
    for key in preserve_keys:
        if key in st.session_state:
            preserved[key] = st.session_state[key]

    # Clear all
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Restore preserved
    for key, value in preserved.items():
        st.session_state[key] = value

    logger.info("Session state cleared")


def save_state_to_disk(filepath: Optional[str] = None) -> Path:
    """Save current session state to disk for recovery.

    Args:
        filepath: Optional custom filepath

    Returns:
        Path to saved state file
    """
    if filepath is None:
        state_dir = Path("data/session_states")
        state_dir.mkdir(parents=True, exist_ok=True)
        session_id = get_state('session_id', 'unknown')
        filepath = state_dir / f"state_{session_id}.pkl"

    filepath = Path(filepath)

    # Prepare serializable state
    state_dict = {}
    for key in st.session_state:
        try:
            # Skip non-serializable objects
            if key not in ['current_script']:  # Script objects might not be pickleable
                state_dict[key] = st.session_state[key]
        except Exception as e:
            logger.warning(f"Skipping non-serializable key: {key}")

    try:
        with open(filepath, 'wb') as f:
            pickle.dump(state_dict, f)
        logger.info(f"State saved to: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
        raise


def load_state_from_disk(filepath: str) -> bool:
    """Load session state from disk.

    Args:
        filepath: Path to state file

    Returns:
        True if successful, False otherwise
    """
    filepath = Path(filepath)

    if not filepath.exists():
        logger.warning(f"State file not found: {filepath}")
        return False

    try:
        with open(filepath, 'rb') as f:
            state_dict = pickle.load(f)

        for key, value in state_dict.items():
            st.session_state[key] = value

        logger.info(f"State loaded from: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
        return False


def get_latest_state_file() -> Optional[Path]:
    """Get path to most recent state file.

    Returns:
        Path to latest state file or None
    """
    state_dir = Path("data/session_states")
    if not state_dir.exists():
        return None

    state_files = list(state_dir.glob("state_*.pkl"))
    if not state_files:
        return None

    # Return most recent file
    return max(state_files, key=lambda p: p.stat().st_mtime)
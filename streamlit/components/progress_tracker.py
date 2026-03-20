"""Progress tracking component for multi-step operations."""

import streamlit as st
import time
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track progress for multi-step operations."""

    def __init__(self, total_steps: int, title: str = "Processing..."):
        """Initialize progress tracker.

        Args:
            total_steps: Total number of steps
            title: Progress title
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.title = title

        # Create UI elements
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.detail_text = st.empty()
        self.start_time = time.time()

    def update(self, step: int, message: str, detail: str = "") -> None:
        """Update progress display.

        Args:
            step: Current step number
            message: Status message
            detail: Optional detail message
        """
        self.current_step = step
        progress = min(step / self.total_steps, 1.0)

        self.progress_bar.progress(progress)
        self.status_text.text(f"{self.title}: {message}")

        if detail:
            self.detail_text.caption(detail)

        # Log progress
        logger.debug(f"Progress: {step}/{self.total_steps} - {message}")

    def complete(self, message: str = "Complete!") -> None:
        """Mark progress as complete.

        Args:
            message: Completion message
        """
        elapsed = time.time() - self.start_time
        self.progress_bar.progress(1.0)
        self.status_text.success(f"✅ {message}")
        self.detail_text.caption(f"Completed in {elapsed:.1f} seconds")

        logger.info(f"Progress complete: {message} ({elapsed:.1f}s)")

    def error(self, message: str) -> None:
        """Mark progress as failed.

        Args:
            message: Error message
        """
        self.status_text.error(f"❌ {message}")
        self.detail_text.caption("Operation failed")

        logger.error(f"Progress failed: {message}")

    def clear(self) -> None:
        """Clear progress display."""
        self.progress_bar.empty()
        self.status_text.empty()
        self.detail_text.empty()


def with_progress(func: Callable, total_steps: int = 10,
                 title: str = "Processing...") -> Callable:
    """Decorator to add progress tracking to a function.

    Args:
        func: Function to wrap
        total_steps: Total number of progress steps
        title: Progress title

    Returns:
        Wrapped function with progress tracking
    """
    def wrapper(*args, **kwargs) -> Any:
        tracker = ProgressTracker(total_steps, title)

        try:
            # Pass tracker to function if it accepts it
            import inspect
            sig = inspect.signature(func)
            if 'tracker' in sig.parameters:
                result = func(*args, tracker=tracker, **kwargs)
            else:
                result = func(*args, **kwargs)

            tracker.complete()
            return result

        except Exception as e:
            tracker.error(str(e))
            raise

    return wrapper


def create_step_indicator(steps: list, current_step: int) -> None:
    """Create a visual step indicator.

    Args:
        steps: List of step names
        current_step: Current step index (0-based)
    """
    # Create columns for steps
    cols = st.columns(len(steps))

    for i, (col, step_name) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                # Completed step
                st.success(f"✅ {i+1}. {step_name}")
            elif i == current_step:
                # Current step
                st.info(f"⏳ {i+1}. {step_name}")
            else:
                # Pending step
                st.text(f"⭕ {i+1}. {step_name}")


def estimate_time_remaining(current_step: int, total_steps: int,
                          elapsed_time: float) -> Optional[float]:
    """Estimate time remaining for operation.

    Args:
        current_step: Current step number
        total_steps: Total number of steps
        elapsed_time: Time elapsed so far in seconds

    Returns:
        Estimated time remaining in seconds
    """
    if current_step == 0:
        return None

    avg_time_per_step = elapsed_time / current_step
    remaining_steps = total_steps - current_step
    estimated_remaining = avg_time_per_step * remaining_steps

    return estimated_remaining
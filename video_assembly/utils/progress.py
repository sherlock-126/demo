"""
Progress tracking utilities
"""

import time
from typing import Optional, Callable
from tqdm import tqdm


class ProgressTracker:
    """Track and display progress for video operations"""

    def __init__(
        self,
        total: Optional[int] = None,
        description: str = 'Processing',
        disable: bool = False
    ):
        """
        Initialize progress tracker

        Args:
            total: Total number of items
            description: Progress bar description
            disable: Disable progress display
        """
        self.total = total
        self.description = description
        self.disable = disable
        self.pbar: Optional[tqdm] = None
        self.start_time = None
        self.current = 0

    def start(self):
        """Start progress tracking"""
        if not self.disable:
            self.pbar = tqdm(
                total=self.total,
                desc=self.description,
                unit='%' if self.total == 100 else 'items',
                ncols=100
            )
        self.start_time = time.time()

    def update(self, amount: int = 1):
        """
        Update progress

        Args:
            amount: Amount to increment
        """
        self.current += amount
        if self.pbar:
            self.pbar.update(amount)

    def set_progress(self, value: float):
        """
        Set progress to specific value

        Args:
            value: Progress value (0-100 for percentage)
        """
        if self.pbar:
            delta = value - self.current
            if delta > 0:
                self.pbar.update(delta)
                self.current = value

    def set_description(self, description: str):
        """
        Update progress description

        Args:
            description: New description
        """
        self.description = description
        if self.pbar:
            self.pbar.set_description(description)

    def close(self):
        """Close progress tracker"""
        if self.pbar:
            self.pbar.close()

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start

        Returns:
            Elapsed time in seconds
        """
        if self.start_time:
            return time.time() - self.start_time
        return 0.0

    @staticmethod
    def create_callback(tracker: 'ProgressTracker') -> Callable[[float], None]:
        """
        Create progress callback function

        Args:
            tracker: ProgressTracker instance

        Returns:
            Callback function
        """
        def callback(progress: float):
            tracker.set_progress(progress)
        return callback
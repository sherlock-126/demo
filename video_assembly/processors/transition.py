"""
Transition effects for video assembly
"""

from typing import List, Optional
from ..models import TransitionConfig


class TransitionEngine:
    """Handles transition generation between slides"""

    def __init__(self, config: TransitionConfig):
        """
        Initialize transition engine

        Args:
            config: Transition configuration
        """
        self.config = config

    def calculate_total_duration(
        self,
        num_slides: int,
        slide_duration: float,
        transition_duration: float
    ) -> float:
        """
        Calculate total video duration with transitions

        Args:
            num_slides: Number of slides
            slide_duration: Duration per slide
            transition_duration: Transition duration

        Returns:
            Total duration in seconds
        """
        if num_slides == 0:
            return 0.0

        if num_slides == 1:
            return slide_duration

        # With transitions, slides overlap
        if self.config.type != 'none' and transition_duration > 0:
            total = slide_duration * num_slides
            # Subtract overlap from transitions
            total -= transition_duration * (num_slides - 1)
            return total
        else:
            # No transitions, simple multiplication
            return slide_duration * num_slides

    def get_transition_points(
        self,
        num_slides: int,
        slide_duration: float,
        transition_duration: float
    ) -> List[float]:
        """
        Calculate transition start points

        Args:
            num_slides: Number of slides
            slide_duration: Duration per slide
            transition_duration: Transition duration

        Returns:
            List of transition start times
        """
        if num_slides <= 1 or self.config.type == 'none':
            return []

        points = []
        for i in range(1, num_slides):
            # Transition starts before slide ends
            start = (slide_duration - transition_duration) * i
            points.append(start)

        return points

    def get_easing_function(self) -> str:
        """
        Get FFmpeg easing function name

        Returns:
            FFmpeg easing parameter
        """
        easing_map = {
            'linear': 'linear',
            'ease-in': 'easeIn',
            'ease-out': 'easeOut',
            'ease-in-out': 'easeInOut'
        }
        return easing_map.get(self.config.easing, 'linear')

    def get_transition_type(self) -> str:
        """
        Get FFmpeg transition type

        Returns:
            FFmpeg transition parameter
        """
        transition_map = {
            'fade': 'fade',
            'dissolve': 'dissolve',
            'wipe': 'wipeleft',
            'none': None
        }
        return transition_map.get(self.config.type, 'fade')
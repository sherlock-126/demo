"""
Background renderer component
"""

from PIL import Image, ImageDraw
from typing import Tuple, Dict
from ..utils.colors import hex_to_rgb


class BackgroundRenderer:
    """Render split-screen backgrounds"""

    def __init__(self, width: int, height: int, colors: Dict[str, str]):
        self.width = width
        self.height = height
        self.colors = colors

    def render(self, split_ratio: float = 0.5) -> Image.Image:
        """Render split-screen background"""
        img = Image.new('RGB', (self.width, self.height), hex_to_rgb(self.colors.get('main', '#FFFFFF')))
        draw = ImageDraw.Draw(img)

        # Calculate split position
        split_x = int(self.width * split_ratio)

        # Draw left side (wrong)
        left_color = hex_to_rgb(self.colors.get('wrong', '#FFE8E8'))
        draw.rectangle([(0, 0), (split_x, self.height)], fill=left_color)

        # Draw right side (right)
        right_color = hex_to_rgb(self.colors.get('right', '#E8FFE8'))
        draw.rectangle([(split_x, 0), (self.width, self.height)], fill=right_color)

        # Optional: Add divider line
        divider_color = hex_to_rgb(self.colors.get('divider', '#CCCCCC'))
        draw.line([(split_x, 0), (split_x, self.height)], fill=divider_color, width=2)

        return img

    def render_gradient(self, split_ratio: float = 0.5) -> Image.Image:
        """Render with gradient backgrounds (optional enhancement)"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        split_x = int(self.width * split_ratio)

        # Create gradient effect
        left_start = hex_to_rgb(self.colors.get('wrong', '#FFE8E8'))
        left_end = tuple(int(c * 0.9) for c in left_start)  # Slightly darker

        for y in range(self.height):
            ratio = y / self.height
            color = tuple(int(s + (e - s) * ratio) for s, e in zip(left_start, left_end))
            draw.line([(0, y), (split_x, y)], fill=color)

        # Right side gradient
        right_start = hex_to_rgb(self.colors.get('right', '#E8FFE8'))
        right_end = tuple(int(c * 0.9) for c in right_start)

        for y in range(self.height):
            ratio = y / self.height
            color = tuple(int(s + (e - s) * ratio) for s, e in zip(right_start, right_end))
            draw.line([(split_x, y), (self.width, y)], fill=color)

        return img
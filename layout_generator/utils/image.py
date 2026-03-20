"""
Image manipulation utilities
"""

from PIL import Image, ImageDraw
from typing import Tuple, Optional


def create_rounded_rectangle(size: Tuple[int, int], radius: int, color: str) -> Image.Image:
    """Create a rounded rectangle image"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle
    x, y = size
    draw.rounded_rectangle([(0, 0), (x-1, y-1)], radius=radius, fill=color)

    return img


def resize_image_aspect(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """Resize image maintaining aspect ratio"""
    image.thumbnail(target_size, Image.Resampling.LANCZOS)
    return image


def center_image(image: Image.Image, canvas_size: Tuple[int, int]) -> Tuple[int, int]:
    """Calculate position to center image on canvas"""
    canvas_w, canvas_h = canvas_size
    img_w, img_h = image.size

    x = (canvas_w - img_w) // 2
    y = (canvas_h - img_h) // 2

    return x, y


def apply_drop_shadow(image: Image.Image, offset: Tuple[int, int] = (5, 5),
                     blur_radius: int = 10, shadow_color: str = "#00000080") -> Image.Image:
    """Apply drop shadow to image"""
    # Create shadow layer
    shadow = Image.new('RGBA',
                      (image.width + abs(offset[0]) * 2,
                       image.height + abs(offset[1]) * 2),
                      (0, 0, 0, 0))

    # Place shadow
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle(
        [(abs(offset[0]) + offset[0], abs(offset[1]) + offset[1]),
         (shadow.width - abs(offset[0]) + offset[0],
          shadow.height - abs(offset[1]) + offset[1])],
        fill=shadow_color
    )

    # Combine
    result = Image.new('RGBA', shadow.size, (0, 0, 0, 0))
    result.paste(shadow, (0, 0))
    result.paste(image, (abs(offset[0]), abs(offset[1])), image if image.mode == 'RGBA' else None)

    return result
#!/usr/bin/env python3
"""
Generate icon images for the layout generator using Pillow
"""

from PIL import Image, ImageDraw
from pathlib import Path

def create_x_icon(size=120):
    """Create a red X icon"""
    # Create transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Settings
    padding = size // 6
    line_width = size // 10
    color = (231, 76, 60, 255)  # Red with full opacity

    # Calculate coordinates
    x1 = padding
    y1 = padding
    x2 = size - padding
    y2 = size - padding

    # Draw X shape with thicker lines
    # Draw multiple lines to create thickness
    for offset in range(-line_width//2, line_width//2 + 1):
        # First diagonal
        draw.line([(x1 + offset, y1), (x2 + offset, y2)], fill=color, width=3)
        draw.line([(x1, y1 + offset), (x2, y2 + offset)], fill=color, width=3)

        # Second diagonal
        draw.line([(x1 + offset, y2), (x2 + offset, y1)], fill=color, width=3)
        draw.line([(x1, y2 + offset), (x2, y1 + offset)], fill=color, width=3)

    # Add circle border for better visibility
    draw.ellipse([(5, 5), (size-5, size-5)], outline=color, width=3)

    return img

def create_check_icon(size=120):
    """Create a green checkmark icon"""
    # Create transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Settings
    color = (39, 174, 96, 255)  # Green with full opacity
    line_width = size // 10

    # Calculate checkmark points
    # Start from left middle, go down, then up to top right
    padding = size // 5

    # Define key points for checkmark
    start_x = padding
    start_y = size // 2

    middle_x = size // 2 - padding // 2
    middle_y = size - padding - padding // 2

    end_x = size - padding
    end_y = padding

    # Draw thick checkmark using multiple lines
    points = [
        (start_x, start_y),
        (middle_x, middle_y),
        (end_x, end_y)
    ]

    # Draw the checkmark with thickness
    for offset in range(-line_width//2, line_width//2 + 1):
        # First segment
        draw.line([
            (points[0][0] + offset, points[0][1]),
            (points[1][0] + offset, points[1][1])
        ], fill=color, width=4)

        draw.line([
            (points[0][0], points[0][1] + offset),
            (points[1][0], points[1][1] + offset)
        ], fill=color, width=4)

        # Second segment
        draw.line([
            (points[1][0] + offset, points[1][1]),
            (points[2][0] + offset, points[2][1])
        ], fill=color, width=4)

        draw.line([
            (points[1][0], points[1][1] + offset),
            (points[2][0], points[2][1] + offset)
        ], fill=color, width=4)

    # Add circle border for better visibility
    draw.ellipse([(5, 5), (size-5, size-5)], outline=color, width=3)

    return img

def create_logo(width=200, height=80):
    """Create a simple text-based logo"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a simple text logo with background
    # Background shape
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=15,
        fill=(44, 62, 80, 230),  # Dark blue with slight transparency
        outline=(52, 152, 219, 255),  # Lighter blue border
        width=2
    )

    # Add text (using default font since we may not have fonts yet)
    text = "DEMO"
    try:
        from PIL import ImageFont
        # Try to use a better font if available
        font_size = height // 2
        font = ImageFont.load_default()

        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw text
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

        # Add subtitle
        subtitle = "Layout Gen"
        bbox = draw.textbbox((0, 0), subtitle, font=font)
        subtitle_width = bbox[2] - bbox[0]
        x = (width - subtitle_width) // 2
        y = height // 2 + 5
        draw.text((x, y), subtitle, fill=(200, 200, 200, 255), font=font)

    except:
        # Fallback if fonts don't work
        draw.text((width//2 - 30, height//2 - 20), "DEMO", fill=(255, 255, 255, 255))
        draw.text((width//2 - 40, height//2), "Layout Gen", fill=(200, 200, 200, 255))

    return img

def main():
    """Generate all icon images"""
    print("Creating icon images...")
    print("=" * 50)

    # Create directories
    icons_dir = Path(__file__).parent.parent / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    logo_dir = Path(__file__).parent.parent / "assets" / "logo"
    logo_dir.mkdir(parents=True, exist_ok=True)

    # Create X icon
    print("Creating X mark icon...")
    x_icon = create_x_icon(120)
    x_icon.save(icons_dir / "x-mark.png", "PNG")
    print(f"Saved: {icons_dir / 'x-mark.png'}")

    # Create check icon
    print("Creating checkmark icon...")
    check_icon = create_check_icon(120)
    check_icon.save(icons_dir / "check-mark.png", "PNG")
    print(f"Saved: {icons_dir / 'check-mark.png'}")

    # Create logo
    print("Creating logo...")
    logo = create_logo(200, 80)
    logo.save(logo_dir / "logo.png", "PNG")
    print(f"Saved: {logo_dir / 'logo.png'}")

    # Also save the placeholder replacement
    logo.save(logo_dir / "placeholder.png", "PNG")
    print(f"Saved: {logo_dir / 'placeholder.png'}")

    print()
    print("=" * 50)
    print("Icon generation complete!")
    print("Created:")
    print("  - x-mark.png (120x120)")
    print("  - check-mark.png (120x120)")
    print("  - logo.png (200x80)")

if __name__ == "__main__":
    main()
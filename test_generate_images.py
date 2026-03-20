#!/usr/bin/env python3
"""
Generate test images for video assembly testing
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_images():
    """Create simple test images for video generation"""
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Create 5 test slides
    for i in range(1, 6):
        # Create a 1080x1920 image (TikTok dimensions)
        img = Image.new('RGB', (1080, 1920), color='white')
        draw = ImageDraw.Draw(img)

        # Split screen - left (wrong) and right (correct)
        # Left side - light red
        draw.rectangle([0, 0, 540, 1920], fill=(255, 230, 230))
        # Right side - light green
        draw.rectangle([540, 0, 1080, 1920], fill=(230, 255, 230))

        # Add text
        try:
            # Try to use a better font, fall back to default if not available
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()

        # Title
        title = f"Slide {i}: Parenting Tip"
        draw.text((540, 100), title, fill='black', font=font_large, anchor='mt')

        # Labels
        draw.text((270, 400), "SAI", fill='red', font=font_large, anchor='mm')
        draw.text((810, 400), "ĐÚNG", fill='green', font=font_large, anchor='mm')

        # Content
        wrong_text = f"Wrong way {i}"
        right_text = f"Right way {i}"
        draw.text((270, 960), wrong_text, fill='darkred', font=font_medium, anchor='mm')
        draw.text((810, 960), right_text, fill='darkgreen', font=font_medium, anchor='mm')

        # Add X and checkmark symbols
        # X mark on left
        draw.line((170, 600, 370, 800), fill='red', width=10)
        draw.line((370, 600, 170, 800), fill='red', width=10)

        # Checkmark on right
        draw.line((710, 700, 780, 800), fill='green', width=10)
        draw.line((780, 800, 910, 600), fill='green', width=10)

        # Save the image
        output_path = os.path.join(output_dir, f'slide_{i}.png')
        img.save(output_path, quality=95)
        print(f"Created {output_path}")

    print(f"\nGenerated {5} test images in {output_dir}/")

if __name__ == "__main__":
    create_test_images()
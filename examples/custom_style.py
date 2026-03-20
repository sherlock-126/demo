#!/usr/bin/env python3
"""
Example: Generate with custom styling
"""

from layout_generator import LayoutGenerator, LayoutConfig
from content_generator.models import ScriptModel, Slide, SideContent
from pathlib import Path


def main():
    # Create custom configuration
    custom_config = {
        "layout": {
            "width": 1080,
            "height": 1920,
            "padding": 40,
            "split_ratio": 0.5
        },
        "colors": {
            "background": {
                "main": "#2C3E50",
                "wrong": "#E8B4B4",
                "right": "#B4E8C8"
            },
            "text": {
                "title": "#FFFFFF",
                "subtitle": "#BDC3C7",
                "label_wrong": "#C0392B",
                "label_right": "#27AE60",
                "content": "#2C3E50"
            }
        },
        "fonts": {
            "title": {"path": "assets/fonts/Roboto-Bold.ttf", "size": 80},
            "subtitle": {"path": "assets/fonts/Roboto-Regular.ttf", "size": 50},
            "label": {"path": "assets/fonts/Roboto-Black.ttf", "size": 65},
            "text": {"path": "assets/fonts/Roboto-Medium.ttf", "size": 45}
        },
        "icons": {
            "wrong": "assets/icons/x-mark.png",
            "right": "assets/icons/check-mark.png",
            "size": 130
        }
    }

    # Initialize with custom config
    generator = LayoutGenerator(config=custom_config)

    # Create a simple script programmatically
    script = ScriptModel(
        topic="Custom Style Demo",
        main_title="PHONG CÁCH TÙY CHỈNH",
        subtitle="Ví dụ về tùy chỉnh giao diện",
        slides=[
            Slide(
                left_side=SideContent(
                    description="Demo wrong side",
                    text="Nội dung sai",
                    label="SAI"
                ),
                right_side=SideContent(
                    description="Demo right side",
                    text="Nội dung đúng",
                    label="ĐÚNG"
                )
            )
        ]
    )

    # Generate with custom style
    print("Generating with custom style...")
    result = generator.generate_from_script(script, output_dir="output/custom")

    print(f"✅ Generated custom styled images")
    print(f"📁 Output: {result.metadata['output_dir']}")

    # Also try different config files
    configs = ["default", "minimal", "colorful"]

    for config_name in configs:
        print(f"\nGenerating with {config_name} style...")
        gen = LayoutGenerator(config=f"config/{config_name}.yaml")
        result = gen.generate_from_script(
            script,
            output_dir=f"output/{config_name}"
        )
        print(f"  ✅ Saved to output/{config_name}/")


if __name__ == "__main__":
    main()
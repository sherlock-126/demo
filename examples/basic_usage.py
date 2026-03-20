#!/usr/bin/env python3
"""
Basic usage example for the Content Generator
"""

from content_generator import ScriptGenerator

def main():
    # Initialize the generator (API key from environment)
    generator = ScriptGenerator()

    # Generate a script
    topic = "Cách dạy con không la mắng khi trẻ mắc lỗi"

    print(f"Generating script for: {topic}")
    script = generator.generate(
        topic=topic,
        num_slides=5,
        language="vi"
    )

    # Display results
    print(f"\nTitle: {script.main_title}")
    print(f"Subtitle: {script.subtitle}")
    print(f"Number of slides: {len(script.slides)}")
    print(f"Tokens used: {script.metadata.tokens_used}")

    # Display each slide
    for i, slide in enumerate(script.slides, 1):
        print(f"\n--- Slide {i} ---")
        print(f"[{slide.left_side.label}] {slide.left_side.text}")
        print(f"[{slide.right_side.label}] {slide.right_side.text}")

    # Export as text
    print("\n" + "="*50)
    print("Text Export:")
    print("="*50)
    text_export = generator.export_script(script, format="text")
    print(text_export)


if __name__ == "__main__":
    main()
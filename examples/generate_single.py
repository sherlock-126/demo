#!/usr/bin/env python3
"""
Example: Generate images from a single script
"""

from layout_generator import LayoutGenerator
from pathlib import Path


def main():
    # Initialize generator with default config
    generator = LayoutGenerator()

    # Path to sample script (from content_generator)
    script_path = Path("examples/sample_output.json")

    if not script_path.exists():
        print(f"Sample script not found at {script_path}")
        print("Please generate a script using content_generator first.")
        return

    # Generate images
    print(f"Generating images from {script_path}...")
    result = generator.generate_from_script(str(script_path))

    # Display results
    print(f"\n✅ Successfully generated {len(result.images)} slides")
    print(f"📁 Output directory: {result.metadata['output_dir']}")
    print("\nGenerated files:")
    for img_path in result.images:
        print(f"  - {Path(img_path).name}")

    if result.thumbnails:
        print("\nThumbnails:")
        for thumb_path in result.thumbnails:
            print(f"  - {Path(thumb_path).name}")


if __name__ == "__main__":
    main()
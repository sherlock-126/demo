#!/usr/bin/env python3
"""
Example: Batch process multiple scripts
"""

from layout_generator import LayoutGenerator
from pathlib import Path
import json


def main():
    # Directory containing JSON scripts
    scripts_dir = Path("data/scripts")
    output_dir = Path("output/batch")

    # Create directories if needed
    scripts_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all JSON files
    json_files = list(scripts_dir.glob("*.json"))

    if not json_files:
        print(f"No JSON scripts found in {scripts_dir}")
        print("Generate some scripts using content_generator first.")
        return

    print(f"Found {len(json_files)} scripts to process")

    # Initialize generator with custom config
    generator = LayoutGenerator(config="config/minimal.yaml")

    # Process each script
    for i, script_file in enumerate(json_files, 1):
        print(f"\n[{i}/{len(json_files)}] Processing {script_file.name}...")

        try:
            # Create subdirectory for each script
            script_output = output_dir / script_file.stem

            # Generate images
            result = generator.generate_from_script(
                str(script_file),
                output_dir=str(script_output)
            )

            print(f"  ✅ Generated {len(result.images)} slides")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n✅ Batch processing complete!")
    print(f"📁 Check {output_dir} for results")


if __name__ == "__main__":
    main()
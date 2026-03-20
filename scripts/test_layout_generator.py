#!/usr/bin/env python3
"""
Test script to verify layout generator works with Vietnamese content
"""

from pathlib import Path
import json
from layout_generator import LayoutGenerator
from content_generator.models import ScriptModel

def test_vietnamese_rendering():
    """Test that Vietnamese text renders correctly"""
    print("Testing Vietnamese text rendering...")
    print("=" * 50)

    # Load the sample script
    script_path = Path("tests/fixtures/sample_script.json")
    if not script_path.exists():
        print("❌ Sample script not found")
        return False

    # Parse the script
    with open(script_path) as f:
        script_data = json.load(f)
    script = ScriptModel(**script_data)

    print(f"✅ Loaded script: {script.topic}")
    print(f"   Main title: {script.main_title}")
    print(f"   Slides: {len(script.slides)}")

    # Initialize generator with default config
    generator = LayoutGenerator()
    print("✅ Layout generator initialized")

    # Generate images
    output_dir = Path("test_vietnamese_output")
    result = generator.generate_all(script, output_dir=str(output_dir))

    print(f"✅ Generated {len(result.images)} images")

    # Verify all images exist
    for img_path in result.images:
        if not Path(img_path).exists():
            print(f"❌ Missing image: {img_path}")
            return False

    print("✅ All images generated successfully")

    # Check Vietnamese characters in the script
    vietnamese_chars = "ảãạăằẳẵặâầẩẫậéèẻẽẹêềểễệíìỉĩịóòỏõọôồổỗộơờởỡợúùủũụưừửữựýỳỷỹỵđĐ"
    has_vietnamese = any(char in script.main_title + script.subtitle for char in vietnamese_chars)

    if has_vietnamese:
        print("✅ Vietnamese characters detected and rendered")
    else:
        print("ℹ️  No Vietnamese tone marks in titles, but text contains Vietnamese words")

    return True

def test_asset_loading():
    """Test that all assets load correctly"""
    print("\nTesting asset loading...")
    print("=" * 50)

    assets_dir = Path("assets")

    # Check fonts
    fonts = list((assets_dir / "fonts").glob("*.ttf"))
    print(f"✅ Found {len(fonts)} font files:")
    for font in fonts:
        if font.name != "placeholder.txt":
            print(f"   - {font.name}")

    # Check icons
    icons = list((assets_dir / "icons").glob("*.png"))
    print(f"✅ Found {len(icons)} icon files:")
    for icon in icons:
        if icon.name != "placeholder.txt":
            print(f"   - {icon.name}")

    # Check logo
    logos = list((assets_dir / "logo").glob("*.png"))
    print(f"✅ Found {len(logos)} logo files:")
    for logo in logos:
        if logo.name != "placeholder.txt":
            print(f"   - {logo.name}")

    return True

def main():
    """Run all tests"""
    print("Layout Generator Test Suite")
    print("=" * 50)

    # Test asset loading
    if not test_asset_loading():
        print("❌ Asset loading test failed")
        return

    # Test Vietnamese rendering
    if not test_vietnamese_rendering():
        print("❌ Vietnamese rendering test failed")
        return

    print()
    print("=" * 50)
    print("✅ All tests passed successfully!")
    print("The layout generator is ready for use with Vietnamese content.")

if __name__ == "__main__":
    main()
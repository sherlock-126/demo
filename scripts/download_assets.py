#!/usr/bin/env python3
"""
Download font assets from Google Fonts for the layout generator
"""

import os
import requests
from pathlib import Path
import zipfile
import shutil

def download_file(url, dest_path):
    """Download a file from URL to destination path"""
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved to {dest_path}")

def download_roboto_fonts():
    """Download Roboto fonts from Google Fonts"""
    fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # Direct download URLs for Roboto fonts
    roboto_base = "https://github.com/google/fonts/raw/main/apache/roboto/static/"

    fonts = {
        "Roboto-Black.ttf": roboto_base + "Roboto-Black.ttf",
        "Roboto-Bold.ttf": roboto_base + "Roboto-Bold.ttf",
        "Roboto-Medium.ttf": roboto_base + "Roboto-Medium.ttf",
        "Roboto-Regular.ttf": roboto_base + "Roboto-Regular.ttf",
    }

    print("Downloading Roboto fonts...")
    for filename, url in fonts.items():
        dest_path = fonts_dir / filename
        if dest_path.exists():
            print(f"{filename} already exists, skipping")
            continue
        try:
            download_file(url, dest_path)
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            # Try alternative method
            print("Trying alternative download method...")
            alt_url = f"https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-{filename.split('-')[1]}"
            try:
                download_file(alt_url, dest_path)
            except:
                print(f"Could not download {filename}, will use system fallback")

def download_noto_sans():
    """Download Noto Sans for Vietnamese support"""
    fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # Download Noto Sans Regular for Vietnamese
    noto_url = "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf"
    dest_path = fonts_dir / "NotoSans-Regular.ttf"

    if dest_path.exists():
        print("NotoSans-Regular.ttf already exists, skipping")
        return

    print("Downloading Noto Sans for Vietnamese support...")
    try:
        # Try the variable font first
        download_file(noto_url, dest_path)
    except:
        # Fallback to static version
        print("Trying static font version...")
        static_url = "https://github.com/google/fonts/raw/main/ofl/notosans/static/NotoSans-Regular.ttf"
        try:
            download_file(static_url, dest_path)
        except Exception as e:
            print(f"Could not download Noto Sans: {e}")
            print("Will use system font as fallback")

def main():
    """Main function to download all assets"""
    print("Starting font download process...")
    print("=" * 50)

    # Download Roboto fonts
    download_roboto_fonts()

    print()

    # Download Noto Sans for Vietnamese
    download_noto_sans()

    print()
    print("=" * 50)
    print("Font download complete!")

    # List downloaded fonts
    fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"
    if fonts_dir.exists():
        fonts = list(fonts_dir.glob("*.ttf"))
        if fonts:
            print(f"Downloaded {len(fonts)} font files:")
            for font in fonts:
                print(f"  - {font.name}")
        else:
            print("No fonts downloaded. Will use system fallbacks.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Validate FFmpeg installation and features
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from video_assembly.ffmpeg import FFmpegValidator


def main():
    """Validate FFmpeg installation"""
    print("FFmpeg Validation")
    print("=" * 50)

    validator = FFmpegValidator()

    try:
        # Validate installation
        validator.validate()
        print("✓ FFmpeg is properly installed!")

        # Get detailed info
        info = validator.get_info()

        print(f"\nVersion: {info.get('version', 'Unknown')}")
        print(f"FFmpeg path: {info.get('ffmpeg_path', 'Unknown')}")
        print(f"FFprobe path: {info.get('ffprobe_path', 'Unknown')}")

        # Check codecs
        print("\nCodecs:")
        codecs = info.get('codecs', {})
        required_codecs = ['libx264', 'aac', 'mp3']
        for codec in required_codecs:
            status = '✓' if codecs.get(codec) else '✗'
            print(f"  {status} {codec}")

        # Check filters
        print("\nFilters:")
        filters = info.get('filters', [])
        required_filters = ['scale', 'pad', 'fade', 'afade', 'concat', 'format']
        for filter_name in required_filters:
            status = '✓' if filter_name in filters else '✗'
            print(f"  {status} {filter_name}")

        print("\n✓ All checks passed! FFmpeg is ready for video generation.")

    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        print("\nTo install FFmpeg:")
        print("  Linux: Run ./scripts/install_ffmpeg.sh")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://www.gyan.dev/ffmpeg/builds/")
        sys.exit(1)


if __name__ == '__main__':
    main()
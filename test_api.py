#!/usr/bin/env python3
"""
Test the video assembly Python API
"""
from video_assembly import create_video, VideoConfig

# Test with simple API
print("Testing simple API...")
result = create_video(
    image_dir='output/',
    output_path='videos/api_test.mp4',
    music_path='audio/background.mp3'
)

print(f"\nVideo created successfully!")
print(f"Output: {result.output_path}")
print(f"Duration: {result.duration}s")
print(f"File size: {result.file_size} bytes")
print(f"Images used: {len(result.images_used)}")
print(f"Encoding time: {result.encoding_time:.1f}s")

# Test with custom config
print("\n\nTesting with custom configuration...")
config = VideoConfig()
config.timing.duration_per_slide = 4.0
config.timing.transition_duration = 1.0
config.fps = 30
config.encoding.preset = 'fast'

from video_assembly import VideoAssembler
assembler = VideoAssembler(config)

result2 = assembler.create_video(
    image_dir='output/',
    output_path='videos/custom_test.mp4',
    music_path='audio/background.mp3',
    show_progress=False
)

print(f"\nCustom video created!")
print(f"Output: {result2.output_path}")
print(f"Duration: {result2.duration}s")
print(f"Configuration used: {config.fps}fps, {config.timing.duration_per_slide}s per slide")
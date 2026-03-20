"""
Simple example of creating a video from images
"""

from video_assembly import create_video, VideoConfig

# Simple usage with defaults
result = create_video(
    image_dir='output/',
    output_path='videos/my_video.mp4',
    music_path='audio/background.mp3'
)

print(f"Video created: {result.output_path}")
print(f"Duration: {result.duration}s")
print(f"File size: {result.file_size} bytes")

# With custom configuration
config = VideoConfig(
    width=1080,
    height=1920,
    fps=30
)
config.timing.duration_per_slide = 4.0
config.transitions.transition_duration = 1.0

from video_assembly import VideoAPI

api = VideoAPI(config)
result = api.generate_video(
    image_directory='output/',
    music_file='audio/upbeat.mp3'
)

print(f"Custom video created: {result.output_path}")
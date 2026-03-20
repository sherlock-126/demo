"""
Example of custom transition effects
"""

from video_assembly import VideoAPI, VideoConfig

# Configure custom transitions
config = VideoConfig()
config.timing.duration_per_slide = 3.5
config.transitions.type = 'fade'
config.transitions.transition_duration = 0.8
config.transitions.easing = 'ease-in-out'

# Create API with custom config
api = VideoAPI(config)

# Generate video with smooth transitions
result = api.generate_video(
    image_directory='output/',
    output_path='videos/smooth_transitions.mp4',
    music_file='audio/calm.mp3'
)

print(f"Video with custom transitions: {result.output_path}")

# Try different transition settings
config.transitions.type = 'dissolve'
config.transitions.transition_duration = 0.3
config.transitions.easing = 'linear'

api2 = VideoAPI(config)
result2 = api2.generate_video(
    image_directory='output/',
    output_path='videos/quick_transitions.mp4'
)

print(f"Video with quick transitions: {result2.output_path}")
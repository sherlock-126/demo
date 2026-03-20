"""
Example of generating carousel frames for TikTok
"""

from video_assembly import VideoAPI

# Initialize API
api = VideoAPI()

# Generate carousel frames
print("Generating carousel frames...")
frames = api.generate_carousel(
    image_directory='output/',
    output_directory='carousel/'
)

print(f"\nGenerated {len(frames)} frames:")
for i, frame in enumerate(frames, 1):
    print(f"  Frame {i}: {frame}")

print("\nYou can now upload these frames to TikTok as a carousel post!")
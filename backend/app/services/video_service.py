"""Service wrapper for video_assembly module"""

import sys
import os
from typing import List, Optional
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, "/app")

from video_assembly.assembler import VideoAssembler
from video_assembly.models import VideoConfig
from app.core.config import settings
from app.core.tasks import Task


class VideoService:
    """Service for video assembly"""

    def __init__(self):
        self.assembler = VideoAssembler()

    async def create_video(
        self,
        task: Task,
        image_paths: List[str],
        music_path: Optional[str] = None,
        duration_per_slide: float = 3.0,
        transition_duration: float = 0.5
    ) -> str:
        """Create video from images"""
        try:
            # Validate image paths
            for path in image_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Image not found: {path}")

            # Ensure videos directory exists
            os.makedirs(settings.videos_dir, exist_ok=True)

            # Generate output filename
            import uuid
            video_id = str(uuid.uuid4())
            output_path = os.path.join(settings.videos_dir, f"{video_id}.mp4")

            # Create video config
            config = VideoConfig(
                images=image_paths,
                output_path=output_path,
                duration_per_slide=duration_per_slide,
                transition_duration=transition_duration,
                audio_path=music_path,
                resolution=(1080, 1920),
                fps=30
            )

            # Progress callback
            def update_progress(progress: int):
                task.update_progress(progress)

            # Create video with progress tracking
            self.assembler.create_video(
                config=config,
                progress_callback=update_progress
            )

            task.update_progress(100)
            return output_path

        except Exception as e:
            raise Exception(f"Video assembly failed: {str(e)}")


# Global service instance
video_service = VideoService()
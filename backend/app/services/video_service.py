"""
Video generation service
"""
import logging
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class VideoService:
    """Service for video generation operations"""

    def __init__(self):
        self.videos_dir = Path("/app/videos")
        self.output_dir = Path("/app/output")
        self.tasks = {}  # Track async video generation tasks

    async def create_video_async(
        self,
        script_id: str,
        video_id: str,
        music_path: Optional[str] = None,
        duration_per_slide: float = 3.0
    ):
        """Create video asynchronously"""
        try:
            self.tasks[video_id] = {
                "status": "processing",
                "progress": 0
            }

            # Import video assembly module
            try:
                from video_assembly import VideoAssembler

                # Create video assembler
                assembler = VideoAssembler()

                # Get images directory
                images_dir = self.output_dir / script_id
                output_path = self.videos_dir / f"{video_id}.mp4"
                self.videos_dir.mkdir(parents=True, exist_ok=True)

                # Generate video
                result = assembler.create_video(
                    image_dir=str(images_dir),
                    output_path=str(output_path),
                    music_path=music_path
                )

                self.tasks[video_id] = {
                    "status": "completed",
                    "file_path": str(output_path),
                    "duration": result.get("duration", 0)
                }
            except ImportError:
                # Mock implementation
                await asyncio.sleep(5)  # Simulate video generation
                output_path = self.videos_dir / f"{video_id}.mp4"
                self.videos_dir.mkdir(parents=True, exist_ok=True)

                # Create a dummy file for testing
                output_path.touch()

                self.tasks[video_id] = {
                    "status": "completed",
                    "file_path": str(output_path),
                    "duration": duration_per_slide * 5  # Mock duration
                }
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            self.tasks[video_id] = {
                "status": "failed",
                "error": str(e)
            }

    async def get_video_status(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video generation status"""
        task = self.tasks.get(video_id)
        if task:
            return {
                "id": video_id,
                "script_id": "",  # Would need to track this
                "status": task["status"],
                "file_path": task.get("file_path"),
                "duration": task.get("duration")
            }

        # Check if video file exists
        video_path = self.videos_dir / f"{video_id}.mp4"
        if video_path.exists():
            return {
                "id": video_id,
                "script_id": "",
                "status": "completed",
                "file_path": str(video_path)
            }
        return None

    async def list_videos(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List all videos"""
        try:
            self.videos_dir.mkdir(parents=True, exist_ok=True)
            videos = []
            for video_file in sorted(self.videos_dir.glob("*.mp4"))[skip:skip+limit]:
                video_id = video_file.stem
                videos.append({
                    "id": video_id,
                    "status": "completed",
                    "file_path": str(video_file),
                    "size": video_file.stat().st_size
                })
            return videos
        except Exception as e:
            logger.error(f"Error listing videos: {e}")
            return []
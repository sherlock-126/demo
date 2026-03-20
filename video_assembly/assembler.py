"""
Main video assembler class
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from .models import VideoConfig, VideoResult, VideoError
from .ffmpeg import FFmpegValidator, FFmpegCommander, FFmpegExecutor
from .processors import ImageProcessor, AudioProcessor, TransitionEngine
from .utils import FileUtils, MediaInfo, ProgressTracker


class VideoAssembler:
    """Assembles images into video with music and transitions"""

    def __init__(self, config: Optional[VideoConfig] = None):
        """
        Initialize video assembler

        Args:
            config: Video configuration (uses defaults if None)
        """
        self.config = config or VideoConfig()

        # Initialize components
        self.validator = FFmpegValidator()
        # Validate FFmpeg installation first
        self.validator.validate()
        # Pass ffmpeg path to all components
        ffmpeg_path = self.validator.ffmpeg_path
        self.commander = FFmpegCommander(self.config, ffmpeg_path)
        self.executor = FFmpegExecutor(ffmpeg_path)
        self.image_processor = ImageProcessor(
            (self.config.width, self.config.height)
        )
        self.audio_processor = AudioProcessor(ffmpeg_path)
        self.transition_engine = TransitionEngine(self.config.transitions)

    def create_video(
        self,
        image_dir: str,
        output_path: Optional[str] = None,
        music_path: Optional[str] = None,
        show_progress: bool = True
    ) -> VideoResult:
        """
        Create video from images

        Args:
            image_dir: Directory containing images
            output_path: Output video path (auto-generated if None)
            music_path: Optional background music path
            show_progress: Show progress bar

        Returns:
            VideoResult with generation details

        Raises:
            VideoError: If video generation fails
        """
        start_time = time.time()

        # Ensure output directory
        if output_path:
            FileUtils.ensure_directory(os.path.dirname(output_path))
        else:
            output_dir = FileUtils.ensure_directory('videos')
            output_path = FileUtils.generate_output_path(
                str(output_dir), 'video', '.mp4'
            )

        # Create temp directory for processing
        temp_dir = FileUtils.create_temp_directory()

        try:
            # Scan and validate images
            image_files = self.image_processor.scan_directory(image_dir)
            if not image_files:
                raise VideoError(
                    error_type='no_images',
                    message='No valid images found',
                    recoverable=False
                )

            print(f"Found {len(image_files)} images")

            # Calculate video duration
            total_duration = self.transition_engine.calculate_total_duration(
                len(image_files),
                self.config.timing.duration_per_slide,
                self.config.timing.transition_duration
            )

            # Check duration limits
            if total_duration < self.config.timing.min_video_duration:
                # Adjust slide duration to meet minimum
                adjusted_duration = self.config.timing.min_video_duration / len(image_files)
                self.config.timing.duration_per_slide = adjusted_duration
                total_duration = self.config.timing.min_video_duration
                print(f"Adjusted slide duration to {adjusted_duration:.1f}s to meet minimum duration")

            elif total_duration > self.config.timing.max_video_duration:
                # Warn about exceeding TikTok limit
                print(f"Warning: Video duration ({total_duration:.1f}s) exceeds TikTok limit")

            # Process audio if provided
            processed_audio = None
            if music_path and self.audio_processor.validate_audio(music_path):
                print("Processing audio...")
                processed_audio = str(temp_dir / 'processed_audio.aac')
                self.audio_processor.prepare_audio_for_video(
                    music_path,
                    total_duration,
                    processed_audio,
                    self.config.audio.fade_in_duration,
                    self.config.audio.fade_out_duration
                )

            # Build FFmpeg command
            command = self.commander.build_slideshow_command(
                image_files,
                output_path,
                processed_audio,
                str(temp_dir)
            )

            # Create progress tracker
            progress = ProgressTracker(
                total=100,
                description='Encoding video',
                disable=not show_progress
            )
            progress.start()

            # Execute command with progress
            result = self.executor.execute(
                command,
                timeout=300  # 5 minutes timeout
            )

            progress.close()

            # Get output file info
            video_info = MediaInfo.get_video_info(output_path)

            # Create thumbnail
            thumbnail_path = output_path.replace('.mp4', '_thumb.jpg')
            self._create_thumbnail(output_path, thumbnail_path)

            # Prepare result
            encoding_time = time.time() - start_time
            video_result = VideoResult(
                output_path=Path(output_path),
                duration=video_info.get('duration', total_duration),
                frame_count=int(video_info.get('duration', total_duration) * self.config.fps),
                file_size=video_info.get('file_size', 0),
                images_used=image_files,
                music_used=music_path,
                encoding_time=encoding_time,
                metadata={
                    'config': self.config.dict(),
                    'video_info': video_info,
                    'thumbnail': thumbnail_path
                }
            )

            # Save metadata
            self._save_metadata(video_result, output_path)

            print(f"\nVideo created successfully: {output_path}")
            print(f"Duration: {video_result.duration:.1f}s")
            print(f"File size: {FileUtils.get_file_size_readable(output_path)}")
            print(f"Encoding time: {encoding_time:.1f}s")

            return video_result

        finally:
            # Cleanup temp directory
            FileUtils.cleanup_temp_directory(str(temp_dir))

    def create_carousel(
        self,
        image_dir: str,
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Create carousel images (static frames for swiping)

        Args:
            image_dir: Directory containing images
            output_dir: Output directory for carousel frames

        Returns:
            List of output image paths
        """
        # Ensure output directory
        if not output_dir:
            output_dir = 'carousel'
        output_path = FileUtils.ensure_directory(output_dir)

        # Create timestamped subdirectory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        carousel_dir = output_path / timestamp
        carousel_dir.mkdir(parents=True, exist_ok=True)

        # Scan images
        image_files = self.image_processor.scan_directory(image_dir)

        # Process each image
        output_files = []
        for i, img_path in enumerate(image_files, 1):
            output_file = carousel_dir / f'frame_{i:03d}.jpg'

            # Preprocess image to target resolution
            self.image_processor.preprocess_image(
                img_path,
                str(output_file)
            )
            output_files.append(str(output_file))

            print(f"Processed frame {i}/{len(image_files)}")

        print(f"\nCarousel created with {len(output_files)} frames")
        print(f"Output directory: {carousel_dir}")

        return output_files

    def _create_thumbnail(self, video_path: str, output_path: str):
        """Create thumbnail from video"""
        try:
            command = self.commander.build_thumbnail_command(
                video_path, output_path, 1.0
            )
            # Execute directly without progress
            import subprocess
            subprocess.run(command.command, capture_output=True, timeout=5)
        except Exception:
            pass  # Thumbnail is optional

    def _save_metadata(self, result: VideoResult, output_path: str):
        """Save metadata alongside video"""
        try:
            metadata_path = output_path.replace('.mp4', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(result.metadata, f, indent=2, default=str)
        except Exception:
            pass  # Metadata is optional
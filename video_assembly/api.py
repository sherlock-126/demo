"""
Public API for video assembly
"""

from typing import Optional, Union, List
from pathlib import Path

from .models import VideoConfig, VideoResult
from .assembler import VideoAssembler
from .config import ConfigLoader


class VideoAPI:
    """Public API interface for video assembly"""

    def __init__(self, config: Optional[Union[VideoConfig, str, dict]] = None):
        """
        Initialize Video API

        Args:
            config: Can be:
                - VideoConfig object
                - Path to YAML config file (str)
                - Dictionary with configuration
                - None (uses default config)
        """
        if isinstance(config, VideoConfig):
            self.config = config
        elif isinstance(config, str):
            # Load from YAML file
            self.config = ConfigLoader.load_config(config)
        elif isinstance(config, dict):
            # Create from dictionary
            self.config = VideoConfig(**config)
        else:
            # Use default config
            self.config = VideoConfig()

        self.assembler = VideoAssembler(self.config)

    def generate_video(
        self,
        image_directory: str,
        output_path: Optional[str] = None,
        music_file: Optional[str] = None,
        show_progress: bool = True
    ) -> VideoResult:
        """
        Generate video from images

        Args:
            image_directory: Directory containing images
            output_path: Output video path (auto-generated if None)
            music_file: Optional background music file
            show_progress: Show progress bar during encoding

        Returns:
            VideoResult with video information
        """
        return self.assembler.create_video(
            image_dir=image_directory,
            output_path=output_path,
            music_path=music_file,
            show_progress=show_progress
        )

    def generate_carousel(
        self,
        image_directory: str,
        output_directory: Optional[str] = None
    ) -> List[str]:
        """
        Generate carousel frames from images

        Args:
            image_directory: Directory containing images
            output_directory: Output directory for frames

        Returns:
            List of generated frame paths
        """
        return self.assembler.create_carousel(
            image_dir=image_directory,
            output_dir=output_directory
        )

    def validate_setup(self) -> bool:
        """
        Validate FFmpeg installation and configuration

        Returns:
            True if setup is valid
        """
        try:
            from .ffmpeg import FFmpegValidator
            validator = FFmpegValidator()
            validator.validate()
            return True
        except Exception as e:
            print(f"Validation failed: {e}")
            return False


# Convenience function for simple usage
def create_video(
    image_dir: str,
    output_path: Optional[str] = None,
    music_path: Optional[str] = None,
    **config_overrides
) -> VideoResult:
    """
    Quick function to create video

    Args:
        image_dir: Directory with images
        output_path: Output video path
        music_path: Background music path
        **config_overrides: Configuration overrides

    Returns:
        VideoResult
    """
    # Create config with overrides
    config = VideoConfig(**config_overrides) if config_overrides else None

    # Create API and generate video
    api = VideoAPI(config)
    return api.generate_video(image_dir, output_path, music_path)
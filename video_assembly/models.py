"""
Data models for video assembly
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from pathlib import Path
from datetime import datetime


class TimingConfig(BaseModel):
    """Configuration for video timing"""
    duration_per_slide: float = Field(default=3.0, gt=0, description="Seconds per image")
    transition_duration: float = Field(default=0.5, ge=0, description="Seconds for fade transition")
    min_video_duration: float = Field(default=15.0, gt=0, description="Minimum total duration")
    max_video_duration: float = Field(default=60.0, gt=0, description="Maximum total duration (TikTok limit)")


class AudioConfig(BaseModel):
    """Configuration for audio processing"""
    fade_in_duration: float = Field(default=1.0, ge=0, description="Audio fade in duration")
    fade_out_duration: float = Field(default=1.0, ge=0, description="Audio fade out duration")
    normalize: bool = Field(default=True, description="Normalize audio levels")
    target_loudness: int = Field(default=-14, description="Target loudness in LUFS")


class EncodingConfig(BaseModel):
    """Configuration for video encoding"""
    video_codec: str = Field(default='libx264', description="Video codec")
    audio_codec: str = Field(default='aac', description="Audio codec")
    preset: Literal['ultrafast', 'fast', 'medium', 'slow', 'veryslow'] = Field(
        default='medium', description="Encoding speed/quality tradeoff"
    )
    crf: int = Field(default=23, ge=0, le=51, description="Constant Rate Factor (quality)")
    pixel_format: str = Field(default='yuv420p', description="Pixel format for compatibility")
    bitrate: str = Field(default='8M', description="Target bitrate")


class TransitionConfig(BaseModel):
    """Configuration for transitions between slides"""
    type: Literal['fade', 'dissolve', 'wipe', 'none'] = Field(
        default='fade', description="Transition type"
    )
    easing: Literal['linear', 'ease-in', 'ease-out', 'ease-in-out'] = Field(
        default='ease-in-out', description="Easing function"
    )


class VideoConfig(BaseModel):
    """Main video configuration"""
    width: int = Field(default=1080, gt=0, description="Video width in pixels")
    height: int = Field(default=1920, gt=0, description="Video height in pixels")
    fps: int = Field(default=60, gt=0, description="Frames per second")
    timing: TimingConfig = Field(default_factory=TimingConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    encoding: EncodingConfig = Field(default_factory=EncodingConfig)
    transitions: TransitionConfig = Field(default_factory=TransitionConfig)

    @classmethod
    def from_yaml(cls, path: str) -> 'VideoConfig':
        """Load configuration from YAML file"""
        import yaml
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        # Restructure flat YAML into nested config
        config_data = {
            'width': data.get('video', {}).get('width', 1080),
            'height': data.get('video', {}).get('height', 1920),
            'fps': data.get('video', {}).get('fps', 60),
            'timing': data.get('timing', {}),
            'audio': data.get('audio', {}),
            'encoding': data.get('encoding', {}),
            'transitions': data.get('transitions', {})
        }
        return cls(**config_data)


class VideoResult(BaseModel):
    """Result of video generation"""
    output_path: Path
    duration: float = Field(description="Video duration in seconds")
    frame_count: int = Field(description="Total number of frames")
    file_size: int = Field(description="File size in bytes")
    images_used: List[str] = Field(description="List of image files used")
    music_used: Optional[str] = Field(default=None, description="Music file used")
    encoding_time: float = Field(description="Time taken to encode in seconds")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class FFmpegCommand(BaseModel):
    """Represents an FFmpeg command to be executed"""
    command: List[str] = Field(description="Command arguments")
    description: str = Field(description="Human-readable description")
    input_files: List[str] = Field(default_factory=list, description="Input file paths")
    output_file: str = Field(description="Output file path")


class VideoError(Exception):
    """Custom exception for video processing errors"""
    def __init__(
        self,
        error_type: str,
        message: str,
        details: Optional[dict] = None,
        suggestion: Optional[str] = None,
        recoverable: bool = False
    ):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
        self.recoverable = recoverable
        super().__init__(message)
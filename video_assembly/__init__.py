"""
Video Assembly Pipeline for TikTok content
"""

from .models import VideoConfig, VideoResult, VideoError
from .assembler import VideoAssembler
from .api import VideoAPI, create_video
from .config import ConfigLoader

__version__ = '1.0.0'

__all__ = [
    'VideoConfig',
    'VideoResult',
    'VideoError',
    'VideoAssembler',
    'VideoAPI',
    'create_video',
    'ConfigLoader'
]
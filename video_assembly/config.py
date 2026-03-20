"""
Configuration management for video assembly
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from .models import VideoConfig


class ConfigLoader:
    """Load and manage video configuration"""

    DEFAULT_CONFIG_PATH = 'config/video_config.yaml'

    @staticmethod
    def load_config(config_path: Optional[str] = None) -> VideoConfig:
        """
        Load configuration from file

        Args:
            config_path: Path to config file (uses default if None)

        Returns:
            VideoConfig object
        """
        if not config_path:
            config_path = ConfigLoader.DEFAULT_CONFIG_PATH

        if Path(config_path).exists():
            return VideoConfig.from_yaml(config_path)

        # Return default config if file doesn't exist
        return VideoConfig()

    @staticmethod
    def save_config(config: VideoConfig, output_path: str):
        """
        Save configuration to file

        Args:
            config: VideoConfig object
            output_path: Output file path
        """
        # Convert config to dictionary
        config_dict = {
            'video': {
                'width': config.width,
                'height': config.height,
                'fps': config.fps
            },
            'timing': config.timing.dict(),
            'audio': config.audio.dict(),
            'encoding': config.encoding.dict(),
            'transitions': config.transitions.dict()
        }

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save to YAML
        with open(output_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def get_preset(preset_name: str) -> VideoConfig:
        """
        Get configuration preset

        Args:
            preset_name: Name of preset ('fast', 'quality', 'default')

        Returns:
            VideoConfig with preset settings
        """
        presets = {
            'fast': {
                'encoding': {
                    'preset': 'ultrafast',
                    'crf': 28
                },
                'timing': {
                    'transition_duration': 0.3
                }
            },
            'quality': {
                'encoding': {
                    'preset': 'slow',
                    'crf': 18,
                    'bitrate': '12M'
                },
                'timing': {
                    'transition_duration': 0.8
                }
            },
            'default': {}
        }

        preset_data = presets.get(preset_name, {})

        # Create base config
        config = VideoConfig()

        # Apply preset overrides
        if 'encoding' in preset_data:
            for key, value in preset_data['encoding'].items():
                setattr(config.encoding, key, value)
        if 'timing' in preset_data:
            for key, value in preset_data['timing'].items():
                setattr(config.timing, key, value)

        return config
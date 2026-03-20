"""
Configuration management for layout generator
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .models import LayoutConfig, RenderError
from .logger import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """Load and validate configuration"""

    DEFAULT_CONFIG = {
        "layout": {
            "width": 1080,
            "height": 1920,
            "padding": 60,
            "split_ratio": 0.5
        },
        "colors": {
            "background": {
                "main": "#FFFFFF",
                "wrong": "#FFE8E8",
                "right": "#E8FFE8"
            },
            "text": {
                "title": "#2C3E50",
                "subtitle": "#7F8C8D",
                "label_wrong": "#E74C3C",
                "label_right": "#27AE60",
                "content": "#34495E"
            }
        },
        "fonts": {
            "title": {
                "path": "assets/fonts/Roboto-Bold.ttf",
                "size": 72
            },
            "subtitle": {
                "path": "assets/fonts/Roboto-Regular.ttf",
                "size": 48
            },
            "label": {
                "path": "assets/fonts/Roboto-Black.ttf",
                "size": 60
            },
            "text": {
                "path": "assets/fonts/Roboto-Medium.ttf",
                "size": 42
            }
        },
        "icons": {
            "wrong": "assets/icons/x-mark.png",
            "right": "assets/icons/check-mark.png",
            "size": 120
        },
        "logo": {
            "path": "assets/logo/placeholder.png",
            "position": "top-center",
            "size": [200, 80],
            "opacity": 0.9
        }
    }

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> LayoutConfig:
        """Load configuration from file or use defaults"""
        if config_path:
            config_data = cls._load_yaml(config_path)
        else:
            config_data = cls._get_default_config()

        # Validate paths exist
        cls._validate_paths(config_data)

        try:
            return LayoutConfig.from_dict(config_data)
        except Exception as e:
            raise RenderError(
                "CONFIG_ERROR",
                f"Invalid configuration: {str(e)}",
                {"config_path": config_path},
                "Check configuration format"
            )

    @classmethod
    def _load_yaml(cls, path: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # Merge with defaults for missing values
                return cls._merge_configs(cls.DEFAULT_CONFIG, data)
        except FileNotFoundError:
            raise RenderError(
                "CONFIG_NOT_FOUND",
                f"Configuration file not found: {path}",
                {"path": path},
                "Use default config or create config file"
            )
        except yaml.YAMLError as e:
            raise RenderError(
                "CONFIG_PARSE_ERROR",
                f"Failed to parse YAML: {str(e)}",
                {"path": path, "error": str(e)},
                "Fix YAML syntax errors"
            )

    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration"""
        config_dir = Path("config")
        default_path = config_dir / "default.yaml"

        if default_path.exists():
            return cls._load_yaml(str(default_path))

        # Create default config if not exists
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)

        cls.save_default_config(str(default_path))
        return cls.DEFAULT_CONFIG

    @classmethod
    def _merge_configs(cls, default: Dict, custom: Dict) -> Dict:
        """Recursively merge configurations"""
        result = default.copy()

        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    @classmethod
    def _validate_paths(cls, config: Dict[str, Any]):
        """Validate that required paths exist"""
        # For now, just log warnings for missing files
        # In production, we'd want to fail or use fallbacks

        # Check fonts
        if 'fonts' in config:
            for font_name, font_config in config['fonts'].items():
                path = font_config.get('path')
                if path and not Path(path).exists():
                    logger.warning(f"Font file not found: {path}")
                    # Use fallback if specified
                    if 'fallback' in font_config:
                        font_config['path'] = font_config['fallback']

        # Check icons
        if 'icons' in config:
            for icon_type in ['wrong', 'right']:
                path = config['icons'].get(icon_type)
                if path and not Path(path).exists():
                    logger.warning(f"Icon file not found: {path}")

        # Check logo
        if 'logo' in config and config['logo']:
            path = config['logo'].get('path')
            if path and not Path(path).exists():
                logger.warning(f"Logo file not found: {path}")

    @classmethod
    def save_default_config(cls, path: str):
        """Save default configuration to file"""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(cls.DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Default configuration saved to: {path}")
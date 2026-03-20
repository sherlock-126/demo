"""
Media file information utilities
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional


class MediaInfo:
    """Extract information from media files"""

    @staticmethod
    def get_video_info(video_path: str) -> Dict:
        """
        Get video file information

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information
        """
        if not Path(video_path).exists():
            return {}

        try:
            # Try to use ffprobe if available
            try:
                cmd = [
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    '-show_streams',
                    video_path
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return MediaInfo._parse_video_info(data)
            except FileNotFoundError:
                # ffprobe not found, return basic info
                file_stats = Path(video_path).stat()
                return {
                    'file_size': file_stats.st_size,
                    'path': str(video_path),
                    'format': Path(video_path).suffix[1:]
                }
        except Exception:
            pass

        return {}

    @staticmethod
    def get_image_info(image_path: str) -> Dict:
        """
        Get image file information

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with image information
        """
        from PIL import Image

        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'file_size': Path(image_path).stat().st_size
                }
        except Exception:
            return {}

    @staticmethod
    def get_audio_info(audio_path: str) -> Dict:
        """
        Get audio file information

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with audio information
        """
        if not Path(audio_path).exists():
            return {}

        try:
            # Try to use ffprobe if available
            try:
                cmd = [
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    '-show_streams',
                    audio_path
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return MediaInfo._parse_audio_info(data)
            except FileNotFoundError:
                # ffprobe not found, return basic info
                file_stats = Path(audio_path).stat()
                return {
                    'file_size': file_stats.st_size,
                    'path': str(audio_path),
                    'format': Path(audio_path).suffix[1:],
                    'duration': 30.0  # Default duration estimate
                }
        except Exception:
            pass

        return {}

    @staticmethod
    def _parse_video_info(probe_data: Dict) -> Dict:
        """Parse ffprobe video data"""
        info = {
            'duration': 0.0,
            'width': 0,
            'height': 0,
            'fps': 0,
            'codec': 'unknown',
            'bitrate': 0,
            'file_size': 0
        }

        # Get format info
        if 'format' in probe_data:
            fmt = probe_data['format']
            info['duration'] = float(fmt.get('duration', 0))
            info['bitrate'] = int(fmt.get('bit_rate', 0))
            info['file_size'] = int(fmt.get('size', 0))

        # Get video stream info
        for stream in probe_data.get('streams', []):
            if stream.get('codec_type') == 'video':
                info['width'] = stream.get('width', 0)
                info['height'] = stream.get('height', 0)
                info['codec'] = stream.get('codec_name', 'unknown')

                # Calculate FPS
                fps_str = stream.get('r_frame_rate', '0/1')
                try:
                    num, den = map(int, fps_str.split('/'))
                    info['fps'] = num / den if den > 0 else 0
                except Exception:
                    info['fps'] = 0
                break

        return info

    @staticmethod
    def _parse_audio_info(probe_data: Dict) -> Dict:
        """Parse ffprobe audio data"""
        info = {
            'duration': 0.0,
            'codec': 'unknown',
            'bitrate': 0,
            'sample_rate': 0,
            'channels': 0,
            'file_size': 0
        }

        # Get format info
        if 'format' in probe_data:
            fmt = probe_data['format']
            info['duration'] = float(fmt.get('duration', 0))
            info['bitrate'] = int(fmt.get('bit_rate', 0))
            info['file_size'] = int(fmt.get('size', 0))

        # Get audio stream info
        for stream in probe_data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                info['codec'] = stream.get('codec_name', 'unknown')
                info['sample_rate'] = int(stream.get('sample_rate', 0))
                info['channels'] = stream.get('channels', 0)
                break

        return info
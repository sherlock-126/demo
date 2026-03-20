"""
FFmpeg availability and feature validation
"""

import subprocess
import re
from typing import Optional, Dict, List
from ..models import VideoError


class FFmpegValidator:
    """Validates FFmpeg installation and features"""

    def __init__(self):
        self.ffmpeg_path: Optional[str] = None
        self.ffprobe_path: Optional[str] = None
        self.version: Optional[str] = None
        self.codecs: Dict[str, bool] = {}
        self.filters: List[str] = []

    def validate(self) -> bool:
        """
        Validate FFmpeg installation and required features

        Returns:
            bool: True if FFmpeg is properly installed

        Raises:
            VideoError: If FFmpeg is not available or missing features
        """
        # Check FFmpeg executable
        if not self._check_executable('ffmpeg'):
            raise VideoError(
                error_type='ffmpeg_not_found',
                message='FFmpeg is not installed or not in PATH',
                suggestion='Install FFmpeg: Ubuntu/Debian: apt-get install ffmpeg, MacOS: brew install ffmpeg',
                recoverable=False
            )

        # Check FFprobe executable (optional - warn if not found)
        if not self._check_executable('ffprobe'):
            print("Warning: FFprobe not found. Some features may be limited.")
            # Don't fail, as basic video generation can work without ffprobe

        # Check version
        self._check_version()

        # Check required codecs
        self._check_codecs()

        # Check required filters
        self._check_filters()

        return True

    def _check_executable(self, name: str) -> bool:
        """Check if executable exists"""
        # Try imageio_ffmpeg first
        if name == 'ffmpeg':
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                result = subprocess.run(
                    [ffmpeg_path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.ffmpeg_path = ffmpeg_path
                    return True
            except:
                pass

        # Try system path
        try:
            result = subprocess.run(
                [name, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                if name == 'ffmpeg':
                    self.ffmpeg_path = name
                elif name == 'ffprobe':
                    self.ffprobe_path = name
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False

    def _check_version(self):
        """Extract FFmpeg version"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path or 'ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Extract version from output
            match = re.search(r'ffmpeg version (\S+)', result.stdout)
            if match:
                self.version = match.group(1)

                # Check minimum version (4.0)
                version_parts = re.findall(r'\d+', self.version)
                if version_parts:
                    major = int(version_parts[0])
                    if major < 4:
                        raise VideoError(
                            error_type='ffmpeg_version',
                            message=f'FFmpeg version {self.version} is too old',
                            details={'current': self.version, 'required': '4.0+'},
                            suggestion='Update FFmpeg to version 4.0 or newer',
                            recoverable=False
                        )
        except subprocess.TimeoutExpired:
            pass

    def _check_codecs(self):
        """Check for required codecs"""
        required_video = ['libx264', 'h264']
        required_audio = ['aac', 'mp3']

        try:
            # Check video encoders
            result = subprocess.run(
                [self.ffmpeg_path or 'ffmpeg', '-encoders'],
                capture_output=True,
                text=True,
                timeout=5
            )

            for codec in required_video:
                self.codecs[codec] = codec in result.stdout

            # Check audio encoders
            for codec in required_audio:
                self.codecs[codec] = codec in result.stdout

            # Validate required codecs
            if not self.codecs.get('libx264', False):
                raise VideoError(
                    error_type='codec_missing',
                    message='libx264 codec not available',
                    details={'missing': 'libx264'},
                    suggestion='Reinstall FFmpeg with libx264 support',
                    recoverable=False
                )

            if not self.codecs.get('aac', False):
                raise VideoError(
                    error_type='codec_missing',
                    message='AAC codec not available',
                    details={'missing': 'aac'},
                    suggestion='Reinstall FFmpeg with AAC support',
                    recoverable=False
                )

        except subprocess.TimeoutExpired:
            pass

    def _check_filters(self):
        """Check for required filters"""
        required = ['scale', 'pad', 'fade', 'afade', 'concat', 'format']

        try:
            result = subprocess.run(
                [self.ffmpeg_path or 'ffmpeg', '-filters'],
                capture_output=True,
                text=True,
                timeout=5
            )

            for filter_name in required:
                if filter_name in result.stdout:
                    self.filters.append(filter_name)

            # Check all required filters are present
            missing = set(required) - set(self.filters)
            if missing:
                raise VideoError(
                    error_type='filter_missing',
                    message=f'Required FFmpeg filters missing: {", ".join(missing)}',
                    details={'missing': list(missing)},
                    suggestion='Reinstall FFmpeg with full filter support',
                    recoverable=False
                )

        except subprocess.TimeoutExpired:
            pass

    def get_info(self) -> Dict:
        """Get FFmpeg installation info"""
        return {
            'ffmpeg_path': self.ffmpeg_path,
            'ffprobe_path': self.ffprobe_path,
            'version': self.version,
            'codecs': self.codecs,
            'filters': self.filters
        }
"""
Audio processing for video assembly
"""

from pathlib import Path
from typing import Optional, List
import random
from ..ffmpeg import FFmpegExecutor
from ..models import VideoError


class AudioProcessor:
    """Process audio files for video generation"""

    SUPPORTED_FORMATS = {'.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac'}

    def __init__(self, ffmpeg_path: Optional[str] = None):
        """Initialize audio processor"""
        self.ffmpeg_path = ffmpeg_path or self._get_ffmpeg_path() or 'ffmpeg'
        self.executor = FFmpegExecutor(self.ffmpeg_path)

    def _get_ffmpeg_path(self) -> Optional[str]:
        """Get FFmpeg path from imageio if available"""
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except:
            return None

    def scan_audio_directory(self, directory: str) -> List[str]:
        """
        Scan directory for audio files

        Args:
            directory: Directory to scan

        Returns:
            List of audio file paths
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            return []

        audio_files = []
        for ext in self.SUPPORTED_FORMATS:
            audio_files.extend(dir_path.glob(f'*{ext}'))
            audio_files.extend(dir_path.glob(f'*{ext.upper()}'))

        return [str(f) for f in audio_files if f.is_file()]

    def select_random_music(self, audio_dir: str) -> Optional[str]:
        """
        Select random music file from directory

        Args:
            audio_dir: Audio directory path

        Returns:
            Path to selected audio file or None
        """
        audio_files = self.scan_audio_directory(audio_dir)
        if audio_files:
            return random.choice(audio_files)
        return None

    def get_duration(self, audio_path: str) -> float:
        """
        Get audio file duration

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            info = self.executor.probe(audio_path)
            if info and 'format' in info and 'duration' in info['format']:
                return float(info['format']['duration'])
        except Exception:
            pass
        return 0.0

    def validate_audio(self, audio_path: str) -> bool:
        """
        Validate audio file

        Args:
            audio_path: Path to audio file

        Returns:
            True if valid audio file
        """
        if not Path(audio_path).exists():
            return False

        try:
            duration = self.get_duration(audio_path)
            return duration > 0
        except Exception:
            return False

    def prepare_audio_for_video(
        self,
        audio_path: str,
        video_duration: float,
        output_path: str,
        fade_in: float = 1.0,
        fade_out: float = 1.0
    ) -> str:
        """
        Prepare audio file for video (trim/loop as needed)

        Args:
            audio_path: Input audio path
            video_duration: Target video duration
            output_path: Output audio path
            fade_in: Fade in duration
            fade_out: Fade out duration

        Returns:
            Path to processed audio file
        """
        if not self.validate_audio(audio_path):
            raise VideoError(
                error_type='invalid_audio',
                message=f'Invalid audio file: {audio_path}',
                recoverable=True
            )

        audio_duration = self.get_duration(audio_path)

        # Build FFmpeg command for audio processing
        cmd = [self.ffmpeg_path, '-y', '-i', audio_path]

        # Build filter chain
        filters = []

        # Loop if audio is shorter than video
        if audio_duration < video_duration:
            loop_count = int(video_duration / audio_duration) + 1
            filters.append(f'aloop=loop={loop_count}:size=2e+09')

        # Trim to exact duration
        filters.append(f'atrim=0:{video_duration}')

        # Add fades
        if fade_in > 0:
            filters.append(f'afade=in:duration={fade_in}')
        if fade_out > 0:
            fade_start = video_duration - fade_out
            filters.append(f'afade=out:start_time={fade_start}:duration={fade_out}')

        # Apply filters
        if filters:
            cmd.extend(['-af', ','.join(filters)])

        # Output settings
        cmd.extend(['-c:a', 'aac', '-b:a', '192k', output_path])

        # Execute command
        try:
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise VideoError(
                    error_type='audio_processing_failed',
                    message='Failed to process audio file',
                    details={'stderr': result.stderr[-500:]},
                    recoverable=True
                )
        except subprocess.TimeoutExpired:
            raise VideoError(
                error_type='audio_processing_timeout',
                message='Audio processing timed out',
                recoverable=True
            )

        return output_path
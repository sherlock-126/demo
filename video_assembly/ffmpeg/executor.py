"""
FFmpeg command execution and monitoring
"""

import subprocess
import json
import re
import time
from typing import Optional, Dict, Callable
from pathlib import Path
from ..models import FFmpegCommand, VideoError


class FFmpegExecutor:
    """Executes FFmpeg commands with progress monitoring"""

    def __init__(self, ffmpeg_path: Optional[str] = None, progress_callback: Optional[Callable[[float], None]] = None):
        """
        Initialize executor

        Args:
            ffmpeg_path: Path to ffmpeg executable
            progress_callback: Optional callback function for progress updates
        """
        self.ffmpeg_path = ffmpeg_path or self._get_ffmpeg_path() or 'ffmpeg'
        self.progress_callback = progress_callback

    def _get_ffmpeg_path(self) -> Optional[str]:
        """Get FFmpeg path from imageio if available"""
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except:
            return None

    def execute(
        self,
        command: FFmpegCommand,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute FFmpeg command

        Args:
            command: FFmpegCommand object to execute
            timeout: Optional timeout in seconds

        Returns:
            Dict with execution results

        Raises:
            VideoError: If command fails
        """
        start_time = time.time()

        try:
            # First, get total duration if possible (for progress calculation)
            total_duration = self._get_total_duration(command.input_files)

            # Execute command with progress monitoring
            process = subprocess.Popen(
                command.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor progress
            stderr_lines = []
            current_time = 0.0

            while True:
                # Read stderr line (FFmpeg outputs progress here)
                line = process.stderr.readline()
                if not line:
                    break

                stderr_lines.append(line)

                # Parse progress if available
                if total_duration and 'time=' in line:
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                    if time_match:
                        hours, minutes, seconds = time_match.groups()
                        current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        progress = min(current_time / total_duration * 100, 100)

                        if self.progress_callback:
                            self.progress_callback(progress)

            # Wait for process to complete
            return_code = process.wait(timeout=timeout)

            # Get final output
            stdout = process.stdout.read() if process.stdout else ''

            # Check return code
            if return_code != 0:
                error_msg = self._parse_error('\n'.join(stderr_lines))
                raise VideoError(
                    error_type='ffmpeg_execution_failed',
                    message=f'FFmpeg command failed: {error_msg}',
                    details={
                        'return_code': return_code,
                        'stderr': '\n'.join(stderr_lines[-20:]),  # Last 20 lines
                        'command': ' '.join(command.command[:10])  # First 10 args
                    },
                    suggestion=self._suggest_fix(error_msg),
                    recoverable=True
                )

            # Get output file info if it exists
            output_info = {}
            output_path = Path(command.output_file)
            if output_path.exists():
                output_info = self._get_file_info(str(output_path))

            elapsed_time = time.time() - start_time

            return {
                'success': True,
                'elapsed_time': elapsed_time,
                'output_info': output_info,
                'output_path': str(output_path)
            }

        except subprocess.TimeoutExpired:
            process.kill()
            raise VideoError(
                error_type='ffmpeg_timeout',
                message=f'FFmpeg command timed out after {timeout} seconds',
                details={'timeout': timeout},
                suggestion='Try with simpler encoding settings or longer timeout',
                recoverable=True
            )
        except Exception as e:
            if isinstance(e, VideoError):
                raise
            raise VideoError(
                error_type='ffmpeg_unknown_error',
                message=f'Unexpected error during FFmpeg execution: {str(e)}',
                details={'error': str(e)},
                recoverable=False
            )

    def probe(self, file_path: str) -> Dict:
        """
        Probe media file for information

        Args:
            file_path: Path to media file

        Returns:
            Dict with media information
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}
        except FileNotFoundError:
            # ffprobe not available, return basic info
            return {
                'format': {
                    'duration': '30.0'  # Default duration
                }
            }
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            return {}

    def _get_total_duration(self, input_files: list) -> Optional[float]:
        """Get total duration from input files"""
        total = 0.0
        for file_path in input_files:
            if Path(file_path).suffix.lower() in ['.mp3', '.mp4', '.wav', '.aac', '.m4a']:
                info = self.probe(file_path)
                if 'format' in info and 'duration' in info['format']:
                    total += float(info['format']['duration'])
        return total if total > 0 else None

    def _get_file_info(self, file_path: str) -> Dict:
        """Get file information"""
        path = Path(file_path)
        if not path.exists():
            return {}

        info = {
            'file_size': path.stat().st_size,
            'file_name': path.name
        }

        # Get media info
        probe_data = self.probe(file_path)
        if probe_data:
            if 'format' in probe_data:
                info['duration'] = float(probe_data['format'].get('duration', 0))
                info['bit_rate'] = probe_data['format'].get('bit_rate', 0)

            # Get video stream info
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    info['width'] = stream.get('width', 0)
                    info['height'] = stream.get('height', 0)
                    info['fps'] = eval(stream.get('r_frame_rate', '0/1'))
                    info['codec'] = stream.get('codec_name', 'unknown')
                    break

        return info

    def _parse_error(self, stderr: str) -> str:
        """Parse error message from stderr"""
        error_patterns = [
            r'Error.*?: (.*)',
            r'Invalid.*?: (.*)',
            r'Unknown.*?: (.*)',
            r'No such.*?: (.*)',
            r'.*?failed: (.*)'
        ]

        for pattern in error_patterns:
            match = re.search(pattern, stderr, re.MULTILINE)
            if match:
                return match.group(1).strip()

        # Return last non-empty line if no pattern matches
        lines = [l.strip() for l in stderr.split('\n') if l.strip()]
        return lines[-1] if lines else 'Unknown error'

    def _suggest_fix(self, error_msg: str) -> str:
        """Suggest fix based on error message"""
        error_msg_lower = error_msg.lower()

        if 'no such file' in error_msg_lower:
            return 'Check that all input files exist and paths are correct'
        elif 'permission denied' in error_msg_lower:
            return 'Check write permissions for output directory'
        elif 'codec' in error_msg_lower:
            return 'Try using a different codec or reinstall FFmpeg with full codec support'
        elif 'memory' in error_msg_lower:
            return 'Reduce video quality or resolution to use less memory'
        elif 'filter' in error_msg_lower:
            return 'Check filter syntax or try simpler filters'
        elif 'invalid' in error_msg_lower:
            return 'Check command parameters and syntax'
        else:
            return 'Check FFmpeg installation and try with simpler settings'
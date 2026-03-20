"""
FFmpeg command builder
"""

from typing import List, Optional, Dict
from pathlib import Path
from ..models import FFmpegCommand, VideoConfig


class FFmpegCommander:
    """Builds FFmpeg commands for various operations"""

    def __init__(self, config: VideoConfig):
        self.config = config

    def build_slideshow_command(
        self,
        image_files: List[str],
        output_path: str,
        music_path: Optional[str] = None,
        temp_dir: str = '/tmp'
    ) -> FFmpegCommand:
        """
        Build FFmpeg command for creating video slideshow

        Args:
            image_files: List of image file paths
            output_path: Output video path
            music_path: Optional background music path
            temp_dir: Temporary directory for intermediate files

        Returns:
            FFmpegCommand object
        """
        # Create concat list file
        concat_file = Path(temp_dir) / 'concat_list.txt'
        self._create_concat_file(image_files, concat_file)

        # Base command
        cmd = ['ffmpeg', '-y']  # -y for overwrite

        # Build filter complex for slideshow with transitions
        filter_parts = []
        inputs = []

        # Add image inputs with duration
        for i, img in enumerate(image_files):
            cmd.extend([
                '-loop', '1',
                '-t', str(self.config.timing.duration_per_slide),
                '-i', img
            ])
            inputs.append(f'[{i}:v]')

        # Scale and pad each input to target resolution
        scaled_inputs = []
        for i, input_label in enumerate(inputs):
            filter_parts.append(
                f'{input_label}scale={self.config.width}:{self.config.height}:'
                f'force_original_aspect_ratio=decrease,'
                f'pad={self.config.width}:{self.config.height}:'
                f'(ow-iw)/2:(oh-ih)/2:black[v{i}]'
            )
            scaled_inputs.append(f'[v{i}]')

        # Add transitions between images
        if len(scaled_inputs) > 1 and self.config.transitions.type == 'fade':
            # Build transition chain
            transition_duration = self.config.transitions.transition_duration
            offset = self.config.timing.duration_per_slide - transition_duration

            # Start with first video
            current = scaled_inputs[0]

            for i in range(1, len(scaled_inputs)):
                prev = current
                next_input = scaled_inputs[i]
                output = f'[v{i}fade]' if i < len(scaled_inputs) - 1 else '[vout]'

                filter_parts.append(
                    f'{prev}{next_input}xfade=transition=fade:'
                    f'duration={transition_duration}:'
                    f'offset={offset * i}{output}'
                )
                current = output
        else:
            # Simple concatenation without transitions
            concat_filter = ''.join(scaled_inputs) + f'concat=n={len(scaled_inputs)}:v=1:a=0[vout]'
            filter_parts.append(concat_filter)

        # Add audio if provided
        if music_path and Path(music_path).exists():
            cmd.extend(['-i', music_path])

            # Calculate video duration
            total_duration = len(image_files) * self.config.timing.duration_per_slide
            if self.config.transitions.type == 'fade':
                total_duration -= (len(image_files) - 1) * self.config.transitions.transition_duration

            # Add audio filters
            audio_filters = []

            # Trim/loop audio to match video duration
            audio_filters.append(f'aloop=loop=-1:size=2e+09')
            audio_filters.append(f'atrim=0:{total_duration}')

            # Add fade in/out
            if self.config.audio.fade_in_duration > 0:
                audio_filters.append(f'afade=in:duration={self.config.audio.fade_in_duration}')
            if self.config.audio.fade_out_duration > 0:
                fade_start = total_duration - self.config.audio.fade_out_duration
                audio_filters.append(
                    f'afade=out:start_time={fade_start}:duration={self.config.audio.fade_out_duration}'
                )

            # Normalize if requested
            if self.config.audio.normalize:
                audio_filters.append(f'loudnorm=I={self.config.audio.target_loudness}')

            # Add audio filter to command
            audio_filter_str = ','.join(audio_filters)
            filter_parts.append(f'[{len(image_files)}:a]{audio_filter_str}[aout]')

            # Map audio
            has_audio = True
        else:
            has_audio = False

        # Combine all filters
        filter_complex = ';'.join(filter_parts)
        cmd.extend(['-filter_complex', filter_complex])

        # Map outputs
        cmd.extend(['-map', '[vout]'])
        if has_audio:
            cmd.extend(['-map', '[aout]'])

        # Encoding settings
        cmd.extend([
            '-c:v', self.config.encoding.video_codec,
            '-preset', self.config.encoding.preset,
            '-crf', str(self.config.encoding.crf),
            '-pix_fmt', self.config.encoding.pixel_format,
            '-r', str(self.config.fps)
        ])

        if has_audio:
            cmd.extend(['-c:a', self.config.encoding.audio_codec])

        # Output file
        cmd.append(output_path)

        return FFmpegCommand(
            command=cmd,
            description='Create video slideshow with transitions',
            input_files=image_files + ([music_path] if music_path else []),
            output_file=output_path
        )

    def build_thumbnail_command(
        self,
        video_path: str,
        output_path: str,
        timestamp: float = 1.0
    ) -> FFmpegCommand:
        """
        Build command to extract thumbnail from video

        Args:
            video_path: Input video path
            output_path: Output thumbnail path
            timestamp: Time position to extract frame (seconds)

        Returns:
            FFmpegCommand object
        """
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            output_path
        ]

        return FFmpegCommand(
            command=cmd,
            description='Extract video thumbnail',
            input_files=[video_path],
            output_file=output_path
        )

    def build_probe_command(self, file_path: str) -> List[str]:
        """
        Build ffprobe command for media info

        Args:
            file_path: Media file to probe

        Returns:
            Command arguments list
        """
        return [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]

    def _create_concat_file(self, image_files: List[str], output_path: Path):
        """Create concat demuxer file for FFmpeg"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            for img in image_files:
                f.write(f"file '{img}'\n")
                f.write(f"duration {self.config.timing.duration_per_slide}\n")
            # Add last image again for proper duration
            if image_files:
                f.write(f"file '{image_files[-1]}'\n")
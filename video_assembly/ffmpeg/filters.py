"""
FFmpeg filter graph generation
"""

from typing import List, Optional
from ..models import VideoConfig, TransitionConfig


class FilterBuilder:
    """Builds FFmpeg filter graphs"""

    @staticmethod
    def scale_and_pad(
        input_label: str,
        width: int,
        height: int,
        output_label: str
    ) -> str:
        """
        Create scale and pad filter

        Args:
            input_label: Input stream label
            width: Target width
            height: Target height
            output_label: Output stream label

        Returns:
            Filter string
        """
        return (
            f"{input_label}scale={width}:{height}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black{output_label}"
        )

    @staticmethod
    def fade_transition(
        input1: str,
        input2: str,
        duration: float,
        offset: float,
        output_label: str
    ) -> str:
        """
        Create fade transition between two inputs

        Args:
            input1: First input stream
            input2: Second input stream
            duration: Transition duration in seconds
            offset: Offset time for transition
            output_label: Output stream label

        Returns:
            Filter string
        """
        return (
            f"{input1}{input2}xfade=transition=fade:"
            f"duration={duration}:offset={offset}{output_label}"
        )

    @staticmethod
    def audio_normalize(
        input_label: str,
        target_loudness: int,
        output_label: str
    ) -> str:
        """
        Create audio normalization filter

        Args:
            input_label: Input audio stream
            target_loudness: Target loudness in LUFS
            output_label: Output stream label

        Returns:
            Filter string
        """
        return f"{input_label}loudnorm=I={target_loudness}{output_label}"

    @staticmethod
    def audio_fade(
        input_label: str,
        fade_in: float,
        fade_out: float,
        duration: float,
        output_label: str
    ) -> str:
        """
        Create audio fade in/out filter

        Args:
            input_label: Input audio stream
            fade_in: Fade in duration
            fade_out: Fade out duration
            duration: Total audio duration
            output_label: Output stream label

        Returns:
            Filter string
        """
        filters = []

        if fade_in > 0:
            filters.append(f"afade=in:duration={fade_in}")

        if fade_out > 0:
            fade_start = duration - fade_out
            filters.append(f"afade=out:start_time={fade_start}:duration={fade_out}")

        if filters:
            return f"{input_label}{','.join(filters)}{output_label}"
        else:
            return f"{input_label}acopy{output_label}"

    @staticmethod
    def build_slideshow_filter(
        num_images: int,
        config: VideoConfig,
        has_audio: bool = False
    ) -> str:
        """
        Build complete filter graph for slideshow

        Args:
            num_images: Number of input images
            config: Video configuration
            has_audio: Whether audio is included

        Returns:
            Complete filter complex string
        """
        filters = []

        # Scale and pad each image
        for i in range(num_images):
            filters.append(
                FilterBuilder.scale_and_pad(
                    f"[{i}:v]",
                    config.width,
                    config.height,
                    f"[v{i}]"
                )
            )

        # Add transitions if configured
        if config.transitions.type == 'fade' and num_images > 1:
            transition_duration = config.transitions.transition_duration
            slide_duration = config.timing.duration_per_slide

            # Chain transitions
            current = "[v0]"
            for i in range(1, num_images):
                next_input = f"[v{i}]"
                output = f"[v{i}fade]" if i < num_images - 1 else "[vout]"
                offset = (slide_duration - transition_duration) * i

                filters.append(
                    FilterBuilder.fade_transition(
                        current,
                        next_input,
                        transition_duration,
                        offset,
                        output
                    )
                )
                current = output
        else:
            # Simple concatenation
            concat_inputs = ''.join([f"[v{i}]" for i in range(num_images)])
            filters.append(f"{concat_inputs}concat=n={num_images}:v=1:a=0[vout]")

        return ';'.join(filters)
"""
CLI interface for video assembly
"""

import click
import sys
from pathlib import Path
from typing import Optional

from .api import VideoAPI
from .config import ConfigLoader
from .models import VideoError


@click.group()
def cli():
    """Video Assembly Pipeline - Create TikTok videos from images"""
    pass


@cli.command()
@click.argument('image_dir', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output video path')
@click.option('--music', '-m', type=click.Path(exists=True), help='Background music file')
@click.option('--duration-per-slide', '-d', type=float, default=3.0, help='Seconds per slide')
@click.option('--transition', '-t', type=float, default=0.5, help='Transition duration')
@click.option('--preset', type=click.Choice(['fast', 'quality', 'default']), default='default', help='Encoding preset')
@click.option('--config', '-c', type=click.Path(exists=True), help='Config file path')
@click.option('--no-progress', is_flag=True, help='Disable progress bar')
def generate(
    image_dir: str,
    output: Optional[str],
    music: Optional[str],
    duration_per_slide: float,
    transition: float,
    preset: str,
    config: Optional[str],
    no_progress: bool
):
    """Generate video from images in directory"""
    try:
        # Load configuration
        if config:
            video_config = ConfigLoader.load_config(config)
        else:
            video_config = ConfigLoader.get_preset(preset)

        # Apply command line overrides
        video_config.timing.duration_per_slide = duration_per_slide
        video_config.timing.transition_duration = transition

        # Create API instance
        api = VideoAPI(video_config)

        # Generate video
        click.echo(f"Generating video from images in: {image_dir}")
        result = api.generate_video(
            image_directory=image_dir,
            output_path=output,
            music_file=music,
            show_progress=not no_progress
        )

        click.echo(f"\n✓ Video created successfully!")
        click.echo(f"  Output: {result.output_path}")
        click.echo(f"  Duration: {result.duration:.1f}s")
        click.echo(f"  Images used: {len(result.images_used)}")

    except VideoError as e:
        click.echo(f"\n✗ Error: {e.message}", err=True)
        if e.suggestion:
            click.echo(f"  Suggestion: {e.suggestion}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n✗ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1, required=True)
@click.option('--music-dir', type=click.Path(exists=True), help='Directory with music files')
@click.option('--output-dir', '-o', default='videos', help='Output directory')
@click.option('--preset', type=click.Choice(['fast', 'quality', 'default']), default='default', help='Encoding preset')
def batch(input_dirs, music_dir: Optional[str], output_dir: str, preset: str):
    """Batch process multiple image directories"""
    from .processors.audio import AudioProcessor

    # Get configuration
    config = ConfigLoader.get_preset(preset)
    api = VideoAPI(config)

    # Process each directory
    audio_processor = AudioProcessor()
    success_count = 0
    total_count = len(input_dirs)

    for i, image_dir in enumerate(input_dirs, 1):
        click.echo(f"\nProcessing {i}/{total_count}: {image_dir}")

        # Select random music if directory provided
        music_file = None
        if music_dir:
            music_file = audio_processor.select_random_music(music_dir)

        try:
            result = api.generate_video(
                image_directory=image_dir,
                music_file=music_file,
                show_progress=True
            )
            click.echo(f"✓ Success: {result.output_path}")
            success_count += 1
        except Exception as e:
            click.echo(f"✗ Failed: {str(e)}", err=True)

    click.echo(f"\nBatch complete: {success_count}/{total_count} successful")


@cli.command()
@click.argument('image_dir', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output video path')
def preview(image_dir: str, output: Optional[str]):
    """Generate preview video without audio (faster)"""
    try:
        # Use fast preset for preview
        config = ConfigLoader.get_preset('fast')
        api = VideoAPI(config)

        click.echo(f"Generating preview from: {image_dir}")
        result = api.generate_video(
            image_directory=image_dir,
            output_path=output,
            music_file=None,  # No audio for preview
            show_progress=True
        )

        click.echo(f"\n✓ Preview created: {result.output_path}")

    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('image_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='carousel', help='Output directory')
def carousel(image_dir: str, output_dir: str):
    """Generate carousel frames for swiping"""
    try:
        api = VideoAPI()

        click.echo(f"Generating carousel frames from: {image_dir}")
        frames = api.generate_carousel(
            image_directory=image_dir,
            output_directory=output_dir
        )

        click.echo(f"\n✓ Carousel created with {len(frames)} frames")
        click.echo(f"  Output directory: {Path(frames[0]).parent if frames else output_dir}")

    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def validate():
    """Validate FFmpeg installation"""
    try:
        from .ffmpeg import FFmpegValidator

        click.echo("Validating FFmpeg installation...")
        validator = FFmpegValidator()
        validator.validate()

        info = validator.get_info()
        click.echo("\n✓ FFmpeg is properly installed!")
        click.echo(f"  Version: {info.get('version', 'Unknown')}")
        click.echo(f"  Path: {info.get('ffmpeg_path', 'Unknown')}")

        # Check codecs
        codecs = info.get('codecs', {})
        click.echo("\nCodecs:")
        click.echo(f"  libx264 (H.264): {'✓' if codecs.get('libx264') else '✗'}")
        click.echo(f"  aac (Audio): {'✓' if codecs.get('aac') else '✗'}")

    except Exception as e:
        click.echo(f"\n✗ Validation failed: {str(e)}", err=True)
        click.echo("\nTo install FFmpeg:")
        click.echo("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        click.echo("  MacOS: brew install ffmpeg")
        click.echo("  Windows: Download from ffmpeg.org")
        sys.exit(1)


if __name__ == '__main__':
    cli()
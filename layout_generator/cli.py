"""
CLI interface for layout generator
"""

import click
import json
from pathlib import Path
from .api import LayoutGenerator
from .logger import get_logger

logger = get_logger(__name__)


@click.group()
def cli():
    """Layout Generator CLI for TikTok content"""
    pass


@cli.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output directory')
@click.option('--config', '-c', default=None, help='Configuration file path')
def generate(script_path, output, config):
    """Generate images from a script JSON file"""
    try:
        click.echo(f"Loading script from {script_path}...")
        generator = LayoutGenerator(config=config)

        click.echo("Generating slides...")
        result = generator.generate_from_script(script_path, output_dir=output)

        click.echo(f"✅ Successfully generated {len(result.images)} slides")
        click.echo(f"📁 Output directory: {result.metadata['output_dir']}")

        for img_path in result.images:
            click.echo(f"  - {Path(img_path).name}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output', help='Output directory')
@click.option('--config', '-c', default=None, help='Configuration file path')
def batch(input_dir, output_dir, config):
    """Process multiple script files in batch"""
    input_path = Path(input_dir)
    json_files = list(input_path.glob('*.json'))

    if not json_files:
        click.echo(f"No JSON files found in {input_dir}", err=True)
        raise click.Abort()

    click.echo(f"Found {len(json_files)} script files to process")

    generator = LayoutGenerator(config=config)
    success_count = 0
    error_count = 0

    with click.progressbar(json_files, label='Processing scripts') as scripts:
        for script_file in scripts:
            try:
                # Create subdirectory for each script
                script_output = Path(output_dir) / script_file.stem
                result = generator.generate_from_script(
                    str(script_file),
                    output_dir=str(script_output)
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to process {script_file}: {e}")
                error_count += 1

    click.echo(f"\n✅ Processed: {success_count}")
    if error_count > 0:
        click.echo(f"❌ Failed: {error_count}")


@cli.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.option('--slide', '-s', default=1, help='Slide number to preview (1-based)')
@click.option('--config', '-c', default=None, help='Configuration file path')
@click.option('--output', '-o', default=None, help='Save preview to file')
def preview(script_path, slide, config, output):
    """Preview a specific slide without full generation"""
    try:
        generator = LayoutGenerator(config=config)

        # Load script to check slide count
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)

        num_slides = len(script_data.get('slides', []))

        if slide < 1 or slide > num_slides:
            click.echo(f"Invalid slide number. Script has {num_slides} slides.", err=True)
            raise click.Abort()

        click.echo(f"Generating preview for slide {slide}/{num_slides}...")

        img = generator.preview_slide(script_path, slide_index=slide - 1)

        if output:
            img.save(output, quality=95)
            click.echo(f"✅ Preview saved to {output}")
        else:
            # Show image (requires display)
            img.show()
            click.echo("✅ Preview displayed")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--output', '-o', default='config/default.yaml', help='Output path for config file')
def init_config(output):
    """Create a default configuration file"""
    try:
        from .api import LayoutGenerator
        path = LayoutGenerator.create_default_config(output)
        click.echo(f"✅ Default configuration created at {path}")
        click.echo("You can now edit this file to customize the layout style.")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
"""
CLI interface for the content generator
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from .api import ScriptGenerator
from .models import ErrorResponse
from .logger import logger

console = Console()


@click.group()
def cli():
    """Content Generator - AI-powered TikTok script generation"""
    pass


@cli.command()
@click.argument("topic")
@click.option("--slides", "-s", default=5, help="Number of slides (1-10)")
@click.option("--language", "-l", default="vi", help="Language (vi/en)")
@click.option("--output", "-o", help="Output filename")
@click.option("--no-save", is_flag=True, help="Don't save to file")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def generate(topic, slides, language, output, no_save, api_key):
    """Generate a content script from a topic"""
    try:
        console.print(f"[bold blue]Generating script for:[/] {topic}")

        generator = ScriptGenerator(api_key=api_key)
        script = generator.generate(
            topic=topic,
            num_slides=slides,
            language=language,
            save_to_file=not no_save
        )

        # Display results
        console.print(Panel(
            f"[bold green]✓ Script Generated Successfully![/]\n\n"
            f"[bold]Title:[/] {script.main_title}\n"
            f"[bold]Subtitle:[/] {script.subtitle}\n"
            f"[bold]Slides:[/] {len(script.slides)}\n"
            f"[bold]Tokens:[/] {script.metadata.tokens_used}"
        ))

        # Display slides
        for i, slide in enumerate(script.slides, 1):
            console.print(f"\n[bold cyan]Slide {i}:[/]")
            table = Table(show_header=True)
            table.add_column("Side", style="magenta")
            table.add_column("Label", style="yellow")
            table.add_column("Text", style="white")

            table.add_row(
                "Left",
                slide.left_side.label,
                slide.left_side.text
            )
            table.add_row(
                "Right",
                slide.right_side.label,
                slide.right_side.text
            )
            console.print(table)

        # Save to specific output if requested
        if output and not no_save:
            output_path = Path(output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(script.to_json(), f, ensure_ascii=False, indent=2)
            console.print(f"\n[green]Saved to: {output_path}[/]")

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("topics_file", type=click.Path(exists=True))
@click.option("--output-dir", "-d", default="data/scripts", help="Output directory")
@click.option("--slides", "-s", default=5, help="Number of slides per script")
@click.option("--language", "-l", default="vi", help="Language (vi/en)")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def batch(topics_file, output_dir, slides, language, api_key):
    """Generate scripts for multiple topics from a file"""
    try:
        # Read topics
        with open(topics_file, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]

        console.print(f"[bold blue]Processing {len(topics)} topics...[/]")

        generator = ScriptGenerator(api_key=api_key)
        results = generator.generate_batch(
            topics=topics,
            num_slides=slides,
            language=language
        )

        # Display results
        success_count = sum(1 for r in results if r["status"] == "success")
        console.print(
            f"\n[bold]Results:[/] "
            f"[green]{success_count} successful[/], "
            f"[red]{len(results) - success_count} failed[/]"
        )

        # Show summary table
        table = Table(show_header=True)
        table.add_column("Topic", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="white")

        for result in results:
            status_style = "green" if result["status"] == "success" else "red"
            details = (
                result["script"].main_title if result["status"] == "success"
                else result.get("error", "Unknown error")
            )
            table.add_row(
                result["topic"][:50],
                f"[{status_style}]{result['status']}[/]",
                details[:50]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--limit", "-n", default=10, help="Number of scripts to list")
@click.option("--filter", "-f", help="Filter by topic")
def list(limit, filter):
    """List previously generated scripts"""
    try:
        generator = ScriptGenerator()
        scripts = generator.list_scripts(limit=limit, topic_filter=filter)

        if not scripts:
            console.print("[yellow]No scripts found[/]")
            return

        table = Table(show_header=True, title="Generated Scripts")
        table.add_column("Filename", style="cyan")
        table.add_column("Topic", style="white")
        table.add_column("Title", style="green")
        table.add_column("Slides", style="yellow")
        table.add_column("Generated", style="magenta")

        for script in scripts:
            table.add_row(
                script["filename"][:30],
                script["topic"][:30],
                script["main_title"][:40],
                str(script["num_slides"]),
                script.get("generated_at", "Unknown")[:19]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("filename")
@click.option("--format", "-f", default="json", help="Export format (json/text)")
def export(filename, format):
    """Export a script in different formats"""
    try:
        generator = ScriptGenerator()
        script = generator.load_script(filename)

        output = generator.export_script(script, format)

        if format == "json":
            syntax = Syntax(output, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
        else:
            console.print(output)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise click.ClickException(str(e))


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
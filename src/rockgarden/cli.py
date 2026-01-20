"""Command-line interface for rockgarden."""

from pathlib import Path
from typing import Annotated

import typer

from rockgarden.config import Config
from rockgarden.output import build_site

app = typer.Typer(no_args_is_help=True)


@app.command()
def build(
    source: Annotated[
        Path | None,
        typer.Option("--source", "-s", help="Source directory (overrides config)"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory (overrides config)"),
    ] = None,
    config_file: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to config file"),
    ] = None,
) -> None:
    """Build the static site from an Obsidian vault."""
    config = Config.load(config_file)

    source_dir = source or config.site.source
    output_dir = output or config.site.output

    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()

    if not source_dir.exists():
        typer.echo(f"Error: Source directory not found: {source_dir}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Building site from {source_dir}")

    count = build_site(config, source_dir, output_dir)

    typer.echo(f"Built {count} pages to {output_dir}")


@app.command()
def serve() -> None:
    """Serve the built site locally for preview."""
    typer.echo("Not implemented yet")


def main() -> None:
    app()

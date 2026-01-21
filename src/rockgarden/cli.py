"""Command-line interface for rockgarden."""

import http.server
import shutil
import socketserver
from functools import partial
from pathlib import Path
from typing import Annotated

import typer

from rockgarden.config import Config
from rockgarden.output import build_site

app = typer.Typer(no_args_is_help=True)


def _output_dir_has_contents(output_dir: Path) -> bool:
    """Check if output directory exists and has contents."""
    if not output_dir.exists():
        return False
    return any(output_dir.iterdir())


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
    clean: Annotated[
        bool,
        typer.Option("--clean", help="Clean output directory without prompting"),
    ] = False,
) -> None:
    """Build the static site from an Obsidian vault."""
    # If source specified but no config, look for config in source directory
    if config_file is None and source is not None:
        source_config = source / "rockgarden.toml"
        if source_config.exists():
            config_file = source_config

    config = Config.load(config_file)

    source_dir = source or config.site.source
    source_dir = source_dir.resolve()

    # Resolve output relative to source directory if from config
    if output:
        output_dir = output.resolve()
    else:
        output_dir = (source_dir / config.site.output).resolve()

    if not source_dir.exists():
        typer.echo(f"Error: Source directory not found: {source_dir}", err=True)
        raise typer.Exit(1)

    # Handle cleaning output directory
    if _output_dir_has_contents(output_dir):
        if clean:
            shutil.rmtree(output_dir)
        else:
            confirm = typer.confirm(
                f"Output directory {output_dir} exists. Delete contents?"
            )
            if confirm:
                shutil.rmtree(output_dir)
            else:
                raise typer.Exit(0)

    typer.echo(f"Building site from {source_dir}")

    count = build_site(config, source_dir, output_dir)

    typer.echo(f"Built {count} pages to {output_dir}")


@app.command()
def serve(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory to serve"),
    ] = None,
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to serve on"),
    ] = 8000,
    config_file: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to config file"),
    ] = None,
) -> None:
    """Serve the built site locally for preview."""
    config = Config.load(config_file)
    output_dir = output or config.site.output
    output_dir = output_dir.resolve()

    if not output_dir.exists():
        typer.echo(f"Error: Output directory not found: {output_dir}", err=True)
        typer.echo("Run 'rockgarden build' first.", err=True)
        raise typer.Exit(1)

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(output_dir))

    try:
        httpd = socketserver.TCPServer(("", port), handler)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            typer.echo(f"Error: Port {port} is already in use.", err=True)
            typer.echo(f"Try: rockgarden serve -p {port + 1}", err=True)
            raise typer.Exit(1) from None
        raise

    typer.echo(f"Serving {output_dir} at http://localhost:{port}")
    typer.echo("Press Ctrl+C to stop")

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            typer.echo("\nStopping server")


def main() -> None:
    app()

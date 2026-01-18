"""Command-line interface for rockgarden."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def build() -> None:
    """Build the static site from an Obsidian vault."""
    typer.echo("Hello from rockgarden!")


@app.command()
def serve() -> None:
    """Serve the built site locally for preview."""
    typer.echo("Hello from rockgarden!")


def main() -> None:
    app()

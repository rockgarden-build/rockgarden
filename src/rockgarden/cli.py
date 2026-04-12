"""Command-line interface for rockgarden."""

import errno
import http.server
import shutil
import socketserver
import tomllib
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from rockgarden import __version__
from rockgarden.config import Config
from rockgarden.output import build_site
from rockgarden.theme import export_theme, set_theme_name_in_config, validate_theme_name
from rockgarden.validation import validate_config


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"rockgarden {__version__}")
        raise typer.Exit()


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main_callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
) -> None:
    """Rockgarden - A static site generator for Markdown content."""
    pass


def _output_dir_has_contents(output_dir: Path) -> bool:
    """Check if output directory exists and has contents."""
    if not output_dir.exists():
        return False
    return any(output_dir.iterdir())


def _is_in_gitignore(gitignore_path: Path, pattern: str) -> bool:
    """Check if a pattern is already in .gitignore."""
    if not gitignore_path.exists():
        return False
    content = gitignore_path.read_text()
    lines = [line.strip() for line in content.splitlines()]
    return pattern in lines or f"{pattern}/" in lines or f"/{pattern}" in lines


def _add_to_gitignore(gitignore_path: Path, pattern: str) -> None:
    """Add a pattern to .gitignore."""
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if not content.endswith("\n"):
            content += "\n"
    else:
        content = ""
    content += f"{pattern}/\n"
    gitignore_path.write_text(content)


@app.command()
def init(
    directory: Annotated[
        Path,
        typer.Argument(help="Directory to initialize (defaults to current directory)"),
    ] = Path("."),
) -> None:
    """Initialize a new rockgarden project."""
    directory = directory.resolve()

    config_path = directory / "rockgarden.toml"
    if config_path.exists():
        typer.echo(f"Error: {config_path} already exists", err=True)
        raise typer.Exit(1)

    site_name = typer.prompt("Site name", default="My Site")
    source = typer.prompt("Source directory", default="content")
    output = typer.prompt("Output directory", default="_site")

    config_content = f'''[site]
title = "{site_name}"
source = "{source}"
output = "{output}"
clean_urls = true
'''

    config_path.write_text(config_content)
    typer.echo(f"Created {config_path}")

    gitignore_path = directory / ".gitignore"
    gitignore_entries = [output.rstrip("/"), ".rockgarden"]
    missing = [e for e in gitignore_entries if not _is_in_gitignore(gitignore_path, e)]
    if missing:
        labels = ", ".join(f"'{e}/'" for e in missing)
        add_gitignore = typer.confirm(f"Add {labels} to .gitignore?", default=True)
        if add_gitignore:
            for entry in missing:
                _add_to_gitignore(gitignore_path, entry)
            typer.echo(f"Added {labels} to .gitignore")


class _BuildPaths:
    """Resolved paths for a build."""

    def __init__(
        self,
        config: Config,
        source_dir: Path,
        output_dir: Path,
        project_root: Path,
        config_path: Path,
    ) -> None:
        self.config = config
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.project_root = project_root
        self.config_path = config_path


def _resolve_build_paths(
    source: Path | None,
    output: Path | None,
    config_file: Path | None,
) -> _BuildPaths:
    """Resolve config, source, output, and project root from CLI options."""
    if config_file is None and source is not None:
        source_config = source / "rockgarden.toml"
        if source_config.exists():
            config_file = source_config

    config = Config.load(config_file)

    source_dir = source or config.site.source
    source_dir = source_dir.resolve()

    project_root = config_file.parent.resolve() if config_file else Path.cwd()

    if output:
        output_dir = output.resolve()
    else:
        output_dir = config.site.output.resolve()

    if not source_dir.exists():
        typer.echo(f"Error: Source directory not found: {source_dir}", err=True)
        raise typer.Exit(1)

    config_path = (
        config_file.resolve() if config_file else Path("rockgarden.toml").resolve()
    )

    return _BuildPaths(config, source_dir, output_dir, project_root, config_path)


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
    incremental: Annotated[
        bool,
        typer.Option("--incremental", "-i", help="Skip rebuilding unchanged pages"),
    ] = False,
) -> None:
    """Build the static site from Markdown source files."""
    paths = _resolve_build_paths(source, output, config_file)

    if clean and _output_dir_has_contents(paths.output_dir):
        shutil.rmtree(paths.output_dir)

    typer.echo(f"Building site from {paths.source_dir}")

    try:
        result = build_site(
            paths.config,
            paths.source_dir,
            paths.output_dir,
            project_root=paths.project_root,
            incremental=incremental,
            config_path=paths.config_path,
        )
    except Exception as exc:
        _handle_build_error(exc)

    if result.skipped_count:
        typer.echo(
            f"Built {result.page_count} pages"
            f" ({result.skipped_count} unchanged)"
            f" in {result.duration_seconds:.2f}s → {paths.output_dir}"
        )
    else:
        typer.echo(
            f"Built {result.page_count} pages"
            f" in {result.duration_seconds:.2f}s → {paths.output_dir}"
        )

    if result.broken_links:
        total = sum(len(targets) for targets in result.broken_links.values())
        typer.echo(f"\nWarnings: {total} broken link(s) found", err=True)

        for page_slug, targets in sorted(result.broken_links.items()):
            for target in targets:
                typer.echo(f"  {page_slug}: [[{target}]]", err=True)


def _make_handler(
    output_dir: Path,
    base_path: str = "",
) -> type[http.server.SimpleHTTPRequestHandler]:
    """Create an HTTP handler that serves custom 404.html when present."""

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, directory=str(output_dir), **kwargs)  # type: ignore[arg-type]

        def do_GET(self) -> None:
            if base_path:
                self._strip_base_path()
            super().do_GET()

        def _strip_base_path(self) -> None:
            """Strip base_path prefix from request path for local serving."""
            parsed = self.path.split("?", 1)
            url_path = parsed[0]
            if url_path == base_path or url_path == base_path + "/":
                url_path = "/"
            elif url_path.startswith(base_path + "/"):
                url_path = url_path[len(base_path) :]
            self.path = url_path if len(parsed) == 1 else url_path + "?" + parsed[1]

        def send_error(
            self,
            code: int,
            message: str | None = None,
            explain: str | None = None,
        ) -> None:
            if code == 404:
                custom_404 = Path(self.directory) / "404.html"  # type: ignore[attr-defined]
                if custom_404.is_file():
                    body = custom_404.read_bytes()
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
            super().send_error(code, message, explain)

    return _Handler


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

    base_path = config.site.base_path
    handler = _make_handler(output_dir, base_path)

    class ReuseAddrServer(socketserver.TCPServer):
        allow_reuse_address = True

    try:
        httpd = ReuseAddrServer(("", port), handler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            typer.echo(f"Error: Port {port} is already in use.", err=True)
            typer.echo(f"Try: rockgarden serve -p {port + 1}", err=True)
            raise typer.Exit(1) from None
        raise

    url = f"http://localhost:{port}{base_path}/"
    typer.echo(f"Serving {output_dir} at {url}")
    typer.echo("Press Ctrl+C to stop")

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            typer.echo("\nStopping server")


@app.command()
def dev(
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
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to serve on"),
    ] = 8000,
    clean: Annotated[
        bool,
        typer.Option("--clean", help="Clean output directory without prompting"),
    ] = False,
) -> None:
    """Start dev server with live reload."""
    from rockgarden.server import DevServer

    paths = _resolve_build_paths(source, output, config_file)

    if clean and _output_dir_has_contents(paths.output_dir):
        shutil.rmtree(paths.output_dir)

    server = DevServer(
        config=paths.config,
        source_dir=paths.source_dir,
        output_dir=paths.output_dir,
        project_root=paths.project_root,
        config_path=paths.config_path,
        port=port,
    )
    server.start()


icons_app = typer.Typer(no_args_is_help=True, help="Manage icon assets.")
app.add_typer(icons_app, name="icons")


@icons_app.command("update")
def icons_update(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Directory to write icons into"),
    ] = Path("_icons"),
) -> None:
    """Download the latest Lucide icons for local override use."""
    import io
    import json
    import urllib.request
    import zipfile

    api_url = "https://api.github.com/repos/lucide-icons/lucide/releases/latest"
    typer.echo("Fetching latest Lucide release info...")

    req = urllib.request.Request(
        api_url, headers={"Accept": "application/vnd.github.v3+json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        typer.echo(f"Error fetching release info: {e}", err=True)
        raise typer.Exit(1) from None

    tag = data["tag_name"]
    zipball_url = data["zipball_url"]
    typer.echo(f"Downloading Lucide {tag}...")

    try:
        with urllib.request.urlopen(zipball_url) as resp:
            release_data = resp.read()
    except Exception as e:
        typer.echo(f"Error downloading release: {e}", err=True)
        raise typer.Exit(1) from None

    dest = output.resolve() / "lucide"
    dest.mkdir(parents=True, exist_ok=True)

    icon_count = 0
    with zipfile.ZipFile(io.BytesIO(release_data)) as src_zip:
        for entry in src_zip.namelist():
            parts = entry.split("/", 1)
            if len(parts) < 2:
                continue
            rel_path = parts[1]
            if rel_path.startswith("icons/") and rel_path.endswith(".svg"):
                icon_name = rel_path.removeprefix("icons/")
                svg_content = src_zip.read(entry)
                (dest / icon_name).write_bytes(svg_content)
                icon_count += 1
            elif rel_path == "LICENSE":
                (dest / "LICENSE").write_bytes(src_zip.read(entry))

    typer.echo(f"Wrote {icon_count} icons to {dest}")
    typer.echo(f'Add icons_dir = "{output}" to your [build] config to use these icons.')


theme_app = typer.Typer(no_args_is_help=True, help="Manage themes.")
app.add_typer(theme_app, name="theme")


@theme_app.command("export")
def theme_export(
    dir_name: Annotated[
        str,
        typer.Option("--dir", "-d", help="Theme name (created under _themes/)"),
    ] = "default",
) -> None:
    """Export the bundled default theme as a starting point for customization."""
    dest = Path("_themes") / dir_name

    try:
        validate_theme_name(dir_name)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None

    if dest.exists():
        typer.echo(
            f"Error: {dest} already exists. Use --dir for a different name.", err=True
        )
        raise typer.Exit(1)

    try:
        counts = export_theme(dest)
    except Exception as e:
        typer.echo(f"Error exporting theme: {e}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Exported default theme to {dest}/")
    typer.echo(f"  {counts['templates']} templates")
    typer.echo(f"  CSS source: {dest}/static-src/input.css")
    typer.echo(f"  Compiled CSS: {dest}/static/rockgarden.css")
    typer.echo("  Build tooling: tailwind.config.js, package.json")

    config_path = Path("rockgarden.toml")
    if config_path.exists():
        try:
            set_theme_name_in_config(config_path, dir_name)
            typer.echo(f'  Updated rockgarden.toml: [theme] name = "{dir_name}"')
        except Exception as e:
            typer.echo(f"  Warning: could not update rockgarden.toml: {e}", err=True)
    else:
        typer.echo("\nNo rockgarden.toml found. To activate the theme, add:")
        typer.echo(f'  [theme]\n  name = "{dir_name}"')

    typer.echo("\nTo rebuild CSS after editing templates:")
    typer.echo(f"  cd {dest} && npm install && npm run build:css")


@app.command()
def validate(
    source: Annotated[
        Path | None,
        typer.Option("--source", "-s", help="Source directory (to resolve paths)"),
    ] = None,
    config_file: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to config file"),
    ] = None,
) -> None:
    """Validate rockgarden configuration."""
    if config_file is None and source is not None:
        candidate = source / "rockgarden.toml"
        if candidate.exists():
            config_file = candidate

    if config_file is None:
        config_file = Path("rockgarden.toml")

    if not config_file.exists():
        typer.echo(f"Error: config file not found: {config_file}", err=True)
        raise typer.Exit(1)

    try:
        with open(config_file, "rb") as f:
            config_dict = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        typer.echo(f"Error: TOML syntax error in {config_file}: {e}", err=True)
        raise typer.Exit(1) from None

    config_file_dir = config_file.resolve().parent
    resolved_source = source.resolve() if source else None

    issues = validate_config(
        config_dict, source_dir=resolved_source, config_file_dir=config_file_dir
    )

    if not issues:
        typer.echo("✓ No issues found.")
        return

    has_errors = False
    for issue in issues:
        label = "Error" if issue.level == "error" else "Warning"
        typer.echo(f"{label}: {issue.message}", err=True)
        if issue.level == "error":
            has_errors = True

    if has_errors:
        raise typer.Exit(1)


def _handle_build_error(exc: Exception) -> NoReturn:
    import yaml

    if isinstance(exc, yaml.YAMLError):
        typer.echo(f"Error: Invalid YAML in frontmatter: {exc}", err=True)
        typer.echo(
            "Hint: Check your Markdown files for YAML syntax errors in the"
            " frontmatter block (between --- markers).",
            err=True,
        )
    else:
        label = type(exc).__name__
        typer.echo(f"Error: {label}: {exc}", err=True)

    raise typer.Exit(1)


def main() -> None:
    try:
        app()
    except SystemExit:
        raise
    except Exception as exc:
        label = type(exc).__name__
        typer.echo(f"Error: {label}: {exc}", err=True)
        raise SystemExit(1) from None

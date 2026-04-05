"""Dev server orchestrating HTTP serving, file watching, and live reload."""

import socketserver
import threading
from pathlib import Path

import typer

from rockgarden.config import Config
from rockgarden.output import build_site
from rockgarden.output.builder import BuildResult
from rockgarden.server.handler import SSEClients, make_dev_handler
from rockgarden.server.watcher import FileWatcher, classify_changes


class DevServer:
    """Orchestrates HTTP server, file watcher, and SSE notifications."""

    def __init__(
        self,
        config: Config,
        source_dir: Path,
        output_dir: Path,
        project_root: Path,
        config_path: Path,
        port: int = 8000,
    ) -> None:
        self._config = config
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._project_root = project_root
        self._config_path = config_path
        self._port = port
        self._sse_clients = SSEClients()
        self._rebuild_lock = threading.Lock()
        self._dirty = False

    def start(self) -> None:
        """Run initial build, start server and watcher, block until Ctrl+C."""
        result = self._build(incremental=False)
        self._log_build_result(result)

        handler = make_dev_handler(self._output_dir, self._sse_clients)

        class _Server(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            httpd = _Server(("", self._port), handler)
        except OSError as e:
            if e.errno == 48:
                typer.echo(f"Error: Port {self._port} is already in use.", err=True)
                raise typer.Exit(1) from None
            raise

        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        typer.echo(f"Dev server running at http://localhost:{self._port}")
        typer.echo("Watching for changes... (Ctrl+C to stop)")

        watcher = FileWatcher(
            paths=self._watch_paths(),
            on_change=self._on_file_change,
            ignore_paths=self._ignore_paths(),
            debounce=300,
        )
        watcher.start()

        try:
            server_thread.join()
        except KeyboardInterrupt:
            typer.echo("\nStopping dev server")
        finally:
            watcher.stop()
            httpd.shutdown()

    def _watch_paths(self) -> list[Path]:
        """Directories to watch for changes."""
        paths = [self._source_dir]
        root = self._project_root
        for name in [
            "_templates",
            "_macros",
            "_styles",
            "_scripts",
            "_static",
        ]:
            paths.append(root / name)
        theme = self._config.theme.name
        if theme:
            paths.append(root / "_themes" / theme)
        if self._config_path.exists():
            paths.append(self._config_path)
        return paths

    def _ignore_paths(self) -> list[Path]:
        """Paths to exclude from watching."""
        return [
            self._output_dir,
            self._project_root / ".rockgarden",
            self._project_root / ".git",
            self._project_root / "node_modules",
        ]

    def _on_file_change(self, changes: set[tuple[object, str]]) -> None:
        """Called by watcher when files change."""
        changed_paths = [p for _, p in changes]
        display = ", ".join(
            Path(p).relative_to(self._project_root).as_posix()
            if Path(p).is_relative_to(self._project_root)
            else Path(p).name
            for p in changed_paths[:3]
        )
        if len(changed_paths) > 3:
            display += f" (+{len(changed_paths) - 3} more)"
        typer.echo(f"\nChanged: {display}")

        needs_full = classify_changes(
            changes,
            self._source_dir,  # type: ignore[arg-type]
        )
        self._rebuild_with_lock(incremental=not needs_full)

    def _rebuild_with_lock(self, incremental: bool) -> None:
        """Run a rebuild, preventing concurrent builds."""
        if not self._rebuild_lock.acquire(blocking=False):
            self._dirty = True
            return

        try:
            self._do_rebuild(incremental)
            while self._dirty:
                self._dirty = False
                self._do_rebuild(incremental=True)
        finally:
            self._rebuild_lock.release()

    def _do_rebuild(self, incremental: bool) -> None:
        """Execute a single rebuild cycle."""
        try:
            if not incremental:
                self._config = Config.load(
                    self._config_path if self._config_path.exists() else None
                )
            result = self._build(incremental=incremental)
            self._log_build_result(result)
            self._sse_clients.broadcast("reload")
        except Exception as exc:
            label = type(exc).__name__
            typer.echo(f"Build error: {label}: {exc}", err=True)
            self._sse_clients.broadcast("error-build")

    def _build(self, incremental: bool) -> BuildResult:
        """Run the build pipeline."""
        return build_site(
            self._config,
            self._source_dir,
            self._output_dir,
            project_root=self._project_root,
            incremental=incremental,
            config_path=self._config_path,
        )

    def _log_build_result(self, result: BuildResult) -> None:
        """Log build result to console."""
        if result.skipped_count:
            typer.echo(
                f"Built {result.page_count} pages"
                f" ({result.skipped_count} unchanged)"
                f" in {result.duration_seconds:.2f}s"
            )
        else:
            typer.echo(
                f"Built {result.page_count} pages in {result.duration_seconds:.2f}s"
            )

        if result.broken_links:
            total = sum(len(t) for t in result.broken_links.values())
            typer.echo(f"  {total} broken link(s)", err=True)

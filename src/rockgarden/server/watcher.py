"""File watcher using watchfiles for change detection."""

import threading
from collections.abc import Callable
from pathlib import Path

from watchfiles import Change, watch


class FileWatcher:
    """Watch directories for changes and invoke a callback."""

    def __init__(
        self,
        paths: list[Path],
        on_change: Callable[[set[tuple[Change, str]]], None],
        ignore_paths: list[Path] | None = None,
        debounce: int = 300,
    ) -> None:
        self._paths = [p for p in paths if p.exists()]
        self._on_change = on_change
        self._ignore_paths = ignore_paths or []
        self._debounce = debounce
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _make_filter(self) -> Callable[[Change, str], bool]:
        resolved = [str(p.resolve()) + "/" for p in self._ignore_paths]

        def filter_fn(change: Change, path: str) -> bool:
            return not any(path.startswith(prefix) for prefix in resolved)

        return filter_fn

    def _run(self) -> None:
        try:
            for changes in watch(
                *self._paths,
                watch_filter=self._make_filter(),
                debounce=self._debounce,
                stop_event=self._stop_event,
                raise_interrupt=False,
            ):
                if self._stop_event.is_set():
                    break
                self._on_change(changes)
        except Exception:
            pass

    def start(self) -> None:
        """Start watching in a background thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the watcher."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None


def classify_changes(
    changes: set[tuple[Change, str]],
    source_dir: Path,
) -> bool:
    """Classify whether changes require a full rebuild.

    Returns True if any changed file is outside the content source directory
    (i.e., config, templates, macros, styles, scripts, or static files).
    """
    source_prefix = str(source_dir.resolve()) + "/"
    for _change_type, path in changes:
        if not path.startswith(source_prefix):
            return True
    return False

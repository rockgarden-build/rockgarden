"""HTTP handler with SSE live reload and JS injection."""

import http.server
import threading
from importlib.resources import files
from pathlib import Path

_RELOAD_JS = files("rockgarden.server").joinpath("_live_reload.js").read_text("utf-8")
_RELOAD_SCRIPT = f"\n<script>{_RELOAD_JS}</script>\n"
_RELOAD_SCRIPT_BYTES = _RELOAD_SCRIPT.encode("utf-8")


class SSEClients:
    """Thread-safe registry of SSE client connections."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: list[http.server.BaseHTTPRequestHandler] = []

    def add(self, handler: http.server.BaseHTTPRequestHandler) -> None:
        with self._lock:
            self._clients.append(handler)

    def remove(self, handler: http.server.BaseHTTPRequestHandler) -> None:
        with self._lock:
            try:
                self._clients.remove(handler)
            except ValueError:
                pass

    def broadcast(self, event: str, data: str = "") -> None:
        with self._lock:
            clients = list(self._clients)

        dead: list[http.server.BaseHTTPRequestHandler] = []
        msg = f"event: {event}\ndata: {data}\n\n".encode()
        for client in clients:
            try:
                client.wfile.write(msg)
                client.wfile.flush()
            except Exception:
                dead.append(client)

        if dead:
            with self._lock:
                for client in dead:
                    try:
                        self._clients.remove(client)
                    except ValueError:
                        pass


def make_dev_handler(
    output_dir: Path,
    sse_clients: SSEClients,
) -> type[http.server.SimpleHTTPRequestHandler]:
    """Create an HTTP handler with SSE support and live-reload JS injection."""

    class _DevHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, directory=str(output_dir), **kwargs)  # type: ignore[arg-type]

        def do_GET(self) -> None:
            if self.path == "/_rockgarden/events":
                self._handle_sse()
                return

            # Check if this will serve an HTML file so we can inject the script
            path = self.translate_path(self.path)
            fs_path = Path(path)

            # Handle directory → index.html
            if fs_path.is_dir():
                fs_path = fs_path / "index.html"

            if fs_path.is_file() and fs_path.suffix == ".html":
                self._serve_html_with_injection(fs_path)
            else:
                super().do_GET()

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
                    # Inject live reload into 404 page too
                    body = _inject_script(body)
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
            super().send_error(code, message, explain)

        def _handle_sse(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            sse_clients.add(self)
            try:
                # Keep connection open until client disconnects
                while True:
                    # Block on read — will raise when client disconnects
                    data = self.rfile.read(1)
                    if not data:
                        break
            except Exception:
                pass
            finally:
                sse_clients.remove(self)

        def _serve_html_with_injection(self, fs_path: Path) -> None:
            body = fs_path.read_bytes()
            body = _inject_script(body)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            # Suppress default stderr logging
            pass

    return _DevHandler


def _inject_script(body: bytes) -> bytes:
    """Inject live-reload script before </body> in HTML content."""
    marker = b"</body>"
    idx = body.rfind(marker)
    if idx == -1:
        return body + _RELOAD_SCRIPT_BYTES
    return body[:idx] + _RELOAD_SCRIPT_BYTES + body[idx:]

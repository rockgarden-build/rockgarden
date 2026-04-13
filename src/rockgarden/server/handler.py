"""HTTP handler with SSE live reload and JS injection."""

import http.server
import threading
from importlib.resources import files
from pathlib import Path

# Interval for SSE heartbeat comments. Browsers cap concurrent HTTP/1.1
# connections per origin (~6), and an SSE connection holds one slot. If stale
# connections aren't detected promptly, rapid navigation can queue requests
# behind them for tens of seconds. Heartbeats surface a broken pipe on write,
# so stale clients are dropped quickly.
SSE_HEARTBEAT_SECONDS = 10.0

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
    base_path: str = "",
) -> type[http.server.SimpleHTTPRequestHandler]:
    """Create an HTTP handler with SSE support and live-reload JS injection."""

    class _DevHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, directory=str(output_dir), **kwargs)  # type: ignore[arg-type]

        def do_GET(self) -> None:
            if self.path == "/_rockgarden/events":
                self._handle_sse()
                return

            if base_path:
                clean = self.path.split("?", 1)[0]
                under_base = clean == base_path or clean.startswith(base_path + "/")
                if clean == "/" or not under_base:
                    self._serve_base_path_index()
                    return
                self._strip_base_path()

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

        def _strip_base_path(self) -> None:
            """Strip base_path prefix from request path for local serving."""
            parsed = self.path.split("?", 1)
            url_path = parsed[0]
            if url_path == base_path or url_path == base_path + "/":
                url_path = "/"
            elif url_path.startswith(base_path + "/"):
                url_path = url_path[len(base_path) :]
            self.path = url_path if len(parsed) == 1 else url_path + "?" + parsed[1]

        def _serve_base_path_index(self) -> None:
            """Serve an info page at the root pointing to the base_path."""
            body = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<title>Rockgarden Dev Server</title></head><body>"
                f"<p>This site uses <code>base_path</code>: "
                f"<a href='{base_path}/'>{base_path}</a></p>"
                "</body></html>"
            ).encode()
            body = _inject_script(body)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _handle_sse(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            sse_clients.add(self)
            # Short socket timeout so read(1) returns periodically, letting us
            # send heartbeat comments. A failed heartbeat write means the
            # client is gone and this connection can release its slot.
            self.connection.settimeout(SSE_HEARTBEAT_SECONDS)
            try:
                while True:
                    try:
                        data = self.rfile.read(1)
                        if not data:
                            break
                    except TimeoutError:
                        try:
                            self.wfile.write(b": keepalive\n\n")
                            self.wfile.flush()
                        except Exception:
                            break
                    except Exception:
                        break
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

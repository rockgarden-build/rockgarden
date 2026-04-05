"""Tests for the dev server HTTP handler."""

import socketserver
import threading
import urllib.error
import urllib.request

from rockgarden.server.handler import SSEClients, _inject_script, make_dev_handler


def _start_dev_server(output_dir):
    """Start the dev handler on an OS-assigned port."""
    sse_clients = SSEClients()
    handler = make_dev_handler(output_dir, sse_clients)

    class _Server(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = _Server(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port, sse_clients


def test_html_response_includes_live_reload_script(tmp_path):
    output_dir = tmp_path / "_site"
    output_dir.mkdir()
    (output_dir / "index.html").write_text("<html><body><h1>Hello</h1></body></html>")

    httpd, port, _ = _start_dev_server(output_dir)
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
        body = resp.read().decode()
        assert "EventSource" in body
        assert "/_rockgarden/events" in body
        assert "<h1>Hello</h1>" in body
    finally:
        httpd.shutdown()


def test_non_html_response_not_modified(tmp_path):
    output_dir = tmp_path / "_site"
    output_dir.mkdir()
    css_content = "body { color: red; }"
    (output_dir / "style.css").write_text(css_content)

    httpd, port, _ = _start_dev_server(output_dir)
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/style.css")
        body = resp.read().decode()
        assert body == css_content
        assert "EventSource" not in body
    finally:
        httpd.shutdown()


def test_custom_404_includes_live_reload_script(tmp_path):
    output_dir = tmp_path / "_site"
    output_dir.mkdir()
    (output_dir / "404.html").write_text("<html><body><h1>Not Found</h1></body></html>")

    httpd, port, _ = _start_dev_server(output_dir)
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/nonexistent")
        except urllib.error.HTTPError as e:
            assert e.code == 404
            body = e.read().decode()
            assert "Not Found" in body
            assert "EventSource" in body
        else:
            raise AssertionError("Expected 404 HTTPError")
    finally:
        httpd.shutdown()


def test_sse_endpoint_returns_event_stream_headers(tmp_path):
    import socket

    output_dir = tmp_path / "_site"
    output_dir.mkdir()

    httpd, port, _ = _start_dev_server(output_dir)
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=2)
        sock.sendall(b"GET /_rockgarden/events HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        # Read enough of the response to get headers
        data = sock.recv(4096).decode()
        assert "200 OK" in data
        assert "text/event-stream" in data
        assert "no-cache" in data
        sock.close()
    finally:
        httpd.shutdown()


def test_sse_clients_broadcast():
    clients = SSEClients()
    assert len(clients._clients) == 0

    # Broadcast with no clients should not error
    clients.broadcast("reload")


def test_sse_broadcast_delivers_to_client(tmp_path):
    import socket
    import time

    output_dir = tmp_path / "_site"
    output_dir.mkdir()

    httpd, port, sse_clients = _start_dev_server(output_dir)
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=2)
        sock.sendall(b"GET /_rockgarden/events HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        # Read headers
        sock.recv(4096)
        # Give the handler time to register the SSE client
        time.sleep(0.1)

        sse_clients.broadcast("reload", "now")

        sock.settimeout(2)
        data = sock.recv(4096).decode()
        assert "event: reload" in data
        assert "data: now" in data
        sock.close()
    finally:
        httpd.shutdown()


def test_inject_script_before_body():
    html = b"<html><body><h1>Hi</h1></body></html>"
    result = _inject_script(html)
    assert b"EventSource" in result
    assert result.index(b"EventSource") < result.index(b"</body>")


def test_inject_script_no_body_tag():
    html = b"<html><h1>No body tag</h1></html>"
    result = _inject_script(html)
    assert b"EventSource" in result


def test_html_in_subdirectory(tmp_path):
    output_dir = tmp_path / "_site"
    sub = output_dir / "about"
    sub.mkdir(parents=True)
    (sub / "index.html").write_text("<html><body><h1>About</h1></body></html>")

    httpd, port, _ = _start_dev_server(output_dir)
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/about/")
        body = resp.read().decode()
        assert "About" in body
        assert "EventSource" in body
    finally:
        httpd.shutdown()

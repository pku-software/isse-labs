"""Adapter contract checks for mode verification and malformed HTTP responses."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest

import project_adapter


@contextmanager
def status_server(body, code=200, redirect=None):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            if redirect is not None:
                self.send_header("Location", redirect)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(1)


class AdapterTests(unittest.TestCase):
    def test_mode_requires_explicit_mock_and_boolean_external_calls_disabled(self):
        cases = [
            ({"mode": "mock", "external_model_calls": False}, True),
            ({"mode": "real", "external_model_calls": False}, False),
            ({"mode": "mock", "external_model_calls": True}, False),
            ({"mode": "mock", "external_model_calls": 0}, False),
            ({"mode": "mock", "external_model_calls": "false"}, False),
            ({"mode": "mock"}, False),
            ([], False),
        ]
        for payload, expected in cases:
            with self.subTest(payload=payload), status_server(json.dumps(payload).encode()) as (url, requests):
                self.assertIs(project_adapter.confirm_mock_mode(url, 1), expected)
                self.assertEqual(requests, ["/api/lab-status"])

    def test_unavailable_or_invalid_mode_response_is_rejected(self):
        for code, body in [(404, b'{}'), (200, b'not-json'), (200, b'\xff')]:
            with self.subTest(code=code, body=body), status_server(body, code) as (url, _):
                self.assertIs(project_adapter.confirm_mock_mode(url, 1), False)

    def test_mode_redirect_does_not_contact_another_service(self):
        payload = b'{"mode":"mock","external_model_calls":false}'
        with status_server(payload) as (destination, visits):
            with status_server(b'', 302, destination + '/api/lab-status') as (origin, _):
                self.assertIs(project_adapter.confirm_mock_mode(origin, 1), False)
            self.assertEqual(visits, [], "Mode verification must not follow redirects")

    def test_only_a_valid_created_chat_reply_is_successful(self):
        valid = {"id": 1, "message": "监控实验测试消息", "reply": "固定测试回复"}
        self.assertIs(project_adapter.response_is_success(201, json.dumps(valid).encode()), True)
        cases = [
            (200, json.dumps(valid).encode()),
            (503, b'{"error":"simulated failure","code":"mock_failure"}'),
            (201, b'not-json'),
            (201, b'\xff'),
            (201, b'[]'),
            (201, b'null'),
            (201, json.dumps({**valid, "reply": "  "}).encode()),
            (201, json.dumps({**valid, "reply": None}).encode()),
            (201, json.dumps({**valid, "error": "failed"}).encode()),
        ]
        for code, body in cases:
            with self.subTest(code=code, body=body):
                self.assertIs(project_adapter.response_is_success(code, body), False)


if __name__ == "__main__":
    unittest.main()

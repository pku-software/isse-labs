"""Validate HTTP mock checks and rejection before a non-mock chat is sent."""

from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener

import project_adapter as adapter
import simulate_traffic


class AdapterTests(unittest.TestCase):
    def test_request_uses_original_chat_api(self):
        request = adapter.build_chat_request('http://127.0.0.1:5001/', '非敏感测试', 3, True)
        self.assertEqual(request.full_url, 'http://127.0.0.1:5001/api/messages')
        self.assertEqual(request.get_method(), 'POST')
        self.assertEqual(request.get_header('Content-type'), 'application/json')
        self.assertEqual(json.loads(request.data), {
            'message': '非敏感测试', 'mock_delay': 3, 'mock_error': True,
        })

    def test_only_valid_created_records_are_successful(self):
        valid = {'id': 1, 'message': '测试', 'reply': '测试回复'}
        self.assertTrue(adapter.response_is_success(201, json.dumps(valid).encode()))
        for status, body in (
            (503, b'{"error":"Simulated model failure"}'), (200, json.dumps(valid).encode()),
            (201, b'not-json'), (201, b'[]'), (201, b'{"id":1,"message":"test","reply":""}'),
            (201, b'{"id":true,"message":"test","reply":"reply"}'),
        ):
            self.assertFalse(adapter.response_is_success(status, body))

    def test_nonlocal_or_nonroot_addresses_are_refused(self):
        for base in ('http://example.com', 'http://127.0.0.1/api',
                     'http://user:password@127.0.0.1', 'http://127.0.0.1:bad'):
            self.assertFalse(adapter.confirm_mock_mode(base, 0.2))
            with self.assertRaises(ValueError):
                adapter.build_chat_request(base, '测试', 0.1, False)

    def test_status_requires_explicit_flags_and_does_not_redirect(self):
        class StatusHandler(BaseHTTPRequestHandler):
            body = b'{}'
            redirect = False
            redirected_visits = 0

            def log_message(self, *_):
                pass

            def do_GET(self):
                if self.path != '/api/lab/status':
                    type(self).redirected_visits += 1
                self.send_response(302 if self.redirect else 200)
                if self.redirect:
                    # Different host name, same local listener; a redirect must not be followed.
                    self.send_header('Location', f'http://localhost:{self.server.server_port}/unexpected')
                self.end_headers()
                self.wfile.write(self.body)

        server = ThreadingHTTPServer(('127.0.0.1', 0), StatusHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f'http://127.0.0.1:{server.server_port}'
            for status in ({'mode': 'real', 'external_model_calls': True},
                           {'mode': 'mock', 'external_model_calls': 0},
                           {'mode': 'mock'}, [], {'mode': 'mock', 'external_model_calls': False}):
                StatusHandler.body = json.dumps(status).encode()
                expected = isinstance(status, dict) and status.get('external_model_calls') is False
                self.assertEqual(adapter.confirm_mock_mode(base, 2), expected)
            StatusHandler.body = b'not-json'
            self.assertFalse(adapter.confirm_mock_mode(base, 2))
            StatusHandler.redirect = True
            self.assertFalse(adapter.confirm_mock_mode(base, 2))
            self.assertEqual(StatusHandler.redirected_visits, 0)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_actual_real_mode_is_refused_before_chat(self):
        root = Path(__file__).resolve().parent
        runtime = root / '.runtime/app'
        runtime.mkdir(parents=True, exist_ok=True)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        with tempfile.TemporaryDirectory(dir=runtime) as directory:
            with (Path(directory) / 'real-check.log').open('wb') as log:
                process = subprocess.Popen(
                    [sys.executable, str(root / 'app.py'), '--port', str(port)], cwd=root,
                    env=dict(os.environ, CHAT_MODE='real'), stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT,
                )
                try:
                    base = f'http://127.0.0.1:{port}'
                    opener = build_opener(ProxyHandler({}))
                    deadline = time.monotonic() + 5
                    while True:
                        self.assertIsNone(process.poll(), 'Real-mode check service exited')
                        try:
                            with opener.open(base + '/api/hello', timeout=0.2):
                                break
                        except OSError:
                            if time.monotonic() > deadline:
                                self.fail('Real-mode check service did not become ready')
                            time.sleep(0.05)
                    with self.assertRaises(HTTPError) as captured:
                        opener.open(base + '/api/lab/status', timeout=2)
                    self.assertEqual(captured.exception.code, 404)
                    captured.exception.close()
                    self.assertFalse(adapter.confirm_mock_mode(base, 2))
                    output = Path(directory) / 'must-not-be-created.json'
                    with patch.object(adapter, 'build_chat_request') as build:
                        with redirect_stdout(io.StringIO()):
                            code = simulate_traffic.main([
                                '--base-url', base, '--phase-seconds', '1',
                                '--settle-seconds', '0', '--output', str(output),
                            ])
                        self.assertEqual(code, 2)
                        build.assert_not_called()
                    self.assertFalse(output.exists())
                finally:
                    if process.poll() is None:
                        process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()

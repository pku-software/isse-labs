"""通过本机 HTTP 验证适配器的模式检查、重定向拒绝和会话隔离。"""

from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest
from unittest.mock import patch

import project_adapter as adapter
import simulate_traffic


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.state = {'mode': 'mock', 'external_model_calls': False}
        self.redirect = False
        self.visits = []
        self.created = 0
        self.lock = threading.Lock()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                owner.visits.append(self.path)
                if owner.redirect:
                    self.send_response(302)
                    self.send_header('Location', '/redirected')
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(owner.state).encode())

            def do_POST(self):
                owner.visits.append(self.path)
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                with owner.lock:
                    owner.created += 1
                    conversation_id = owner.created
                self.send_response(201)
                self.end_headers()
                self.wfile.write(json.dumps({'id': conversation_id}).encode())

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join, 2)
        self.addCleanup(self.server.shutdown)

    def test_checks_actual_http_state_and_rejects_redirects(self):
        self.assertTrue(adapter.confirm_mock_mode(self.url, 2))
        for state in [{'mode': 'real', 'external_model_calls': True},
                      {'mode': 'mock', 'external_model_calls': True},
                      {'mode': 'mock', 'external_model_calls': 'false'}, {}, []]:
            self.state = state
            self.assertFalse(adapter.confirm_mock_mode(self.url, 2))
        self.redirect = True
        self.assertFalse(adapter.confirm_mock_mode(self.url, 2))
        self.assertNotIn('/redirected', self.visits)
        self.assertFalse(adapter.confirm_mock_mode('http://example.com', 2))

    def test_scheduler_refuses_non_mock_before_sending(self):
        self.state = {'mode': 'real', 'external_model_calls': True}
        with patch.object(adapter, 'ADAPTER_READY', True), patch.object(simulate_traffic, 'run_phase') as run:
            self.assertEqual(simulate_traffic.main(['--base-url', self.url]), 2)
            run.assert_not_called()
        self.assertEqual(self.created, 0)

    def test_workers_use_separate_conversations_and_reuse_their_own(self):
        self.assertTrue(adapter.confirm_mock_mode(self.url, 2))
        barrier = threading.Barrier(2)

        def build():
            first = adapter.build_chat_request(self.url, 'test', 0.1, False)
            barrier.wait(timeout=3)
            second = adapter.build_chat_request(self.url, 'test', 3, True)
            self.assertEqual(first.full_url, second.full_url)
            self.assertEqual(json.loads(second.data), {'message': 'test', 'mock_delay_seconds': 3, 'mock_force_error': True})
            return first.full_url

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(build) for _ in range(2)]
            self.assertEqual(len({f.result() for f in futures}), 2)
        self.assertEqual(self.created, 2)
        with self.assertRaises(ValueError):
            adapter.build_chat_request('http://127.0.0.1:1', 'test', 0.1, False)

    def test_response_requires_valid_business_reply(self):
        good = {'id': 1, 'message': 'test', 'reply': 'mock reply'}
        self.assertTrue(adapter.response_is_success(201, json.dumps(good).encode()))
        for code, body in [(503, good), (200, good), (201, {'error': 'failed'}),
                           (201, {**good, 'reply': ' '}), (201, {**good, 'id': True}), (201, [])]:
            self.assertFalse(adapter.response_is_success(code, json.dumps(body).encode()))
        self.assertFalse(adapter.response_is_success(201, b'not json'))


if __name__ == '__main__':
    unittest.main()

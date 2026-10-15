"""运行：.venv/Scripts/python.exe -m unittest discover -s <个人目录> -v。"""

from concurrent.futures import ThreadPoolExecutor
from itertools import count
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from prometheus_client import REGISTRY

import app as application


def value(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {})


class ChatMonitoringTests(unittest.TestCase):
    def setUp(self):
        runtime = Path(__file__).parent / '.runtime' / 'app'
        runtime.mkdir(parents=True, exist_ok=True)
        self.directory = TemporaryDirectory(dir=runtime)
        self.addCleanup(self.directory.cleanup)
        for name, replacement in {
            'DATA_FILE': Path(self.directory.name) / 'conversations.json',
            'conversations': {}, 'conversation_ids': count(1), 'message_ids': count(1),
            'CHAT_MODE': 'mock',
        }.items():
            replacement_patch = patch.object(application, name, replacement)
            replacement_patch.start()
            self.addCleanup(replacement_patch.stop)
        external = patch.object(application.requests, 'post', side_effect=AssertionError('External call'))
        self.external = external.start()
        self.addCleanup(external.stop)
        application.app.testing = True
        self.addCleanup(setattr, application.app, 'testing', False)
        self.client = application.app.test_client()

    def test_success_and_failure_record_duration_and_finish(self):
        before_success = value('chat_requests_total', {'outcome': 'success'})
        before_error = value('chat_requests_total', {'outcome': 'error'})
        before_count = value('chat_request_duration_seconds_count')
        before_sum = value('chat_request_duration_seconds_sum')
        for failure, status in [(False, 201), (True, 503)]:
            response = self.client.post('/api/messages', json={
                'message': 'test', 'mock_delay_seconds': 0.02, 'mock_force_error': failure,
            })
            self.assertEqual(response.status_code, status)
            self.assertIn('error' if failure else 'reply', response.json)
        self.assertEqual(value('chat_requests_total', {'outcome': 'success'}), before_success + 1)
        self.assertEqual(value('chat_requests_total', {'outcome': 'error'}), before_error + 1)
        self.assertEqual(value('chat_request_duration_seconds_count'), before_count + 2)
        self.assertGreaterEqual(value('chat_request_duration_seconds_sum') - before_sum, 0.04)
        self.assertEqual(value('chat_inprogress_requests'), 0)
        self.external.assert_not_called()

    def test_nonchat_routes_do_not_count_and_crud_is_preserved(self):
        before = value('chat_request_duration_seconds_count')
        for url in ['/', '/metrics', '/api/lab/status', '/api/hello', '/api/conversations']:
            with self.client.get(url) as response:
                self.assertEqual(response.status_code, 200)
        status = self.client.get('/api/lab/status').json
        self.assertEqual(status, {'mode': 'mock', 'external_model_calls': False})
        metrics = self.client.get('/metrics')
        self.assertTrue(metrics.content_type.startswith('text/plain'))
        self.assertIn(b'chat_request_duration_seconds_bucket', metrics.data)
        created = self.client.post('/api/conversations', json={'title': 'test'})
        url = f"/api/conversations/{created.json['id']}"
        self.assertEqual(self.client.patch(url, json={'title': 'renamed'}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(value('chat_request_duration_seconds_count'), before)

    def test_invalid_mock_options_are_rejected_and_gauge_recovers(self):
        for options in [
            {'mock_delay_seconds': -1}, {'mock_delay_seconds': 31},
            {'mock_delay_seconds': True}, {'mock_delay_seconds': '3'},
            {'mock_delay_seconds': float('nan')}, {'mock_delay_seconds': float('inf')},
            {'mock_force_error': 'false'},
        ]:
            with self.subTest(options=options):
                response = self.client.post('/api/messages', json={'message': 'test', **options})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(value('chat_inprogress_requests'), 0)

    def test_validation_and_unhandled_exception_also_finish(self):
        before = value('chat_requests_total', {'outcome': 'error'})
        self.assertEqual(self.client.post('/api/messages', json={'message': ''}).status_code, 400)
        with patch.object(application, 'get_ai_reply', side_effect=RuntimeError('test failure')):
            with self.assertRaises(RuntimeError):
                self.client.post('/api/messages', json={'message': 'test'})
        self.assertEqual(value('chat_requests_total', {'outcome': 'error'}), before + 2)
        self.assertEqual(value('chat_inprogress_requests'), 0)

    def test_real_mode_hides_lab_status_and_ignores_mock_options(self):
        with patch.object(application, 'CHAT_MODE', 'real'), patch.object(
            application, 'get_real_ai_reply', return_value='stubbed real reply'
        ) as real:
            self.assertEqual(self.client.get('/api/lab/status').status_code, 404)
            response = self.client.post('/api/messages', json={
                'message': 'test', 'mock_delay_seconds': -1, 'mock_force_error': True,
            })
            self.assertEqual(response.status_code, 201)
            real.assert_called_once()
        self.external.assert_not_called()

    def test_metrics_remain_responsive_during_concurrent_slow_requests(self):
        ids = [self.client.post('/api/conversations', json={'title': 'concurrency test'}).json['id']
               for _ in range(2)]

        def send(conversation_id, failure):
            with application.app.test_client() as client:
                return client.post(f'/api/conversations/{conversation_id}/messages', json={
                    'message': 'test', 'mock_delay_seconds': 0.8, 'mock_force_error': failure,
                }).status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(send, cid, bool(index)) for index, cid in enumerate(ids)]
            deadline = time.monotonic() + 2
            while value('chat_inprogress_requests') < 2 and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertEqual(value('chat_inprogress_requests'), 2)
            started = time.monotonic()
            self.assertEqual(self.client.get('/metrics').status_code, 200)
            self.assertLess(time.monotonic() - started, 0.5)
            self.assertEqual([future.result() for future in futures], [201, 503])
        self.assertEqual(value('chat_inprogress_requests'), 0)


if __name__ == '__main__':
    unittest.main()

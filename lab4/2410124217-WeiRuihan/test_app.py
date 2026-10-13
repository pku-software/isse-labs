import unittest
from unittest.mock import patch

from prometheus_client import REGISTRY

import app as application


def sample(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {})


class ChatMetricsTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True, CHAT_MODE="mock")
        application.messages.clear()
        self.client = application.app.test_client()

    def test_success_and_failure_record_metrics_without_real_client(self):
        success = sample("chat_requests_total", {"outcome": "success"})
        error = sample("chat_requests_total", {"outcome": "error"})
        count = sample("chat_request_duration_seconds_count")
        duration = sample("chat_request_duration_seconds_sum")
        with patch.object(application, "OpenAI", side_effect=AssertionError("real client used")):
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": 0.01})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json["reply"], "你好")
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": 0.01, "mock_error": True})
            self.assertEqual(response.status_code, 503)
        self.assertEqual(sample("chat_requests_total", {"outcome": "success"}), success + 1)
        self.assertEqual(sample("chat_requests_total", {"outcome": "error"}), error + 1)
        self.assertEqual(sample("chat_request_duration_seconds_count"), count + 2)
        self.assertGreaterEqual(sample("chat_request_duration_seconds_sum") - duration, 0.02)
        self.assertEqual(sample("chat_inprogress_requests"), 0)

    def test_unexpected_exception_also_finishes_metrics(self):
        error = sample("chat_requests_total", {"outcome": "error"})
        count = sample("chat_request_duration_seconds_count")
        with patch.object(application.time, "sleep", side_effect=RuntimeError("test exception")):
            with self.assertRaises(RuntimeError):
                self.client.post("/api/messages", json={"message": "测试"})
        self.assertEqual(sample("chat_requests_total", {"outcome": "error"}), error + 1)
        self.assertEqual(sample("chat_request_duration_seconds_count"), count + 1)
        self.assertEqual(sample("chat_inprogress_requests"), 0)

    def test_auxiliary_routes_do_not_count_and_real_mode_has_no_mock_status(self):
        count = sample("chat_request_duration_seconds_count")
        for route in ("/", "/style.css", "/api/hello", "/api/messages", "/metrics", "/api/lab-status"):
            with self.client.get(route) as response:
                self.assertEqual(response.status_code, 200)
        self.assertEqual(sample("chat_request_duration_seconds_count"), count)
        application.app.config["CHAT_MODE"] = "real"
        self.assertEqual(self.client.get("/api/lab-status").status_code, 404)
        with patch.object(application, "real_reply", return_value=("real test reply", None)) as real:
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": -1, "mock_error": True})
            self.assertEqual(response.status_code, 201)
            real.assert_called_once_with("测试")

    def test_invalid_mock_options_are_rejected(self):
        for delay in (-1, 11, True, "3", float("nan"), float("inf")):
            with self.subTest(delay=delay):
                response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": delay})
                self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/messages", json={"message": "测试", "mock_error": "true"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(sample("chat_inprogress_requests"), 0)


if __name__ == "__main__":
    unittest.main()

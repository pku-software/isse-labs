"""课程调度器验证：临时本地 HTTP 服务，不依赖学生项目或真实模型。

在仓库根目录使用实际 Python 运行 unittest discover -s lab4/tests。
这里的 /test-chat 是测试夹具，绝不是要求学生改用的接口。
"""

from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter"))
import simulate_traffic as traffic


class Handler(BaseHTTPRequestHandler):
    active = 0
    peak = 0
    count = 0
    lock = threading.Lock()

    def do_GET(self):
        body = json.dumps({"mode": "mock", "external_model_calls": False}).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with self.lock:
            Handler.active += 1
            Handler.peak = max(Handler.peak, Handler.active)
            Handler.count += 1
        try:
            time.sleep(data["delay"])
            failed = data["fail"]
            self.send_response(503 if failed else 200)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": not failed}).encode())
        finally:
            with self.lock:
                Handler.active -= 1

    def log_message(self, *args):
        pass


def probe(base_url, timeout):
    with urlopen(base_url + "/test-mode", timeout=timeout) as response:
        data = json.load(response)
    return data["mode"] == "mock" and data["external_model_calls"] is False


def request(base_url, message, delay, fail):
    return Request(base_url + "/test-chat", method="POST",
                   data=json.dumps({"message": message, "delay": delay, "fail": fail}).encode(),
                   headers={"Content-Type": "application/json"})


class TrafficTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_course_adapter_stays_unimplemented(self):
        self.assertFalse(traffic.project_adapter.ADAPTER_READY)
        with self.assertRaises(NotImplementedError):
            traffic.project_adapter.build_chat_request(self.base_url, "test", 0, False)
        with patch.object(traffic.project_adapter, "confirm_mock_mode") as check:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(traffic.main([]), 2)
            check.assert_not_called()

    def test_remote_target_rejected(self):
        for url in ["https://example.com", "http://192.168.1.1", "http://user:pass@localhost", "ftp://localhost"]:
            with self.assertRaises(ValueError):
                traffic.local_origin(url)

    def test_real_mode_rejected_before_chat(self):
        with patch.object(traffic.project_adapter, "ADAPTER_READY", True), \
             patch.object(traffic.project_adapter, "confirm_mock_mode", return_value=False), \
             patch.object(traffic.project_adapter, "build_chat_request") as build:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(traffic.main([]), 2)
            build.assert_not_called()

    def test_all_phases_and_expected_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results" / "test.json"
            with patch.object(traffic.project_adapter, "ADAPTER_READY", True), \
                 patch.object(traffic.project_adapter, "confirm_mock_mode", side_effect=probe), \
                 patch.object(traffic.project_adapter, "build_chat_request", side_effect=request), \
                 patch.object(traffic.project_adapter, "response_is_success", side_effect=lambda code, body: code == 200 and json.loads(body)["ok"]), \
                 redirect_stdout(io.StringIO()):
                code = traffic.main(["--base-url", self.base_url, "--phase-seconds", "0.35",
                                     "--baseline-rate", "20", "--burst-rate", "20", "--slow-rate", "20",
                                     "--slow-delay", "0.2", "--concurrency", "3", "--settle-seconds", "0",
                                     "--output", str(output)])
            self.assertEqual(code, 0)
            phases = json.loads(output.read_text())["phases"]
            self.assertEqual([item["phase"] for item in phases], ["baseline", "burst", "slow", "errors", "recovery"])
            for item in phases:
                self.assertGreater(item["sent"], 0)
                self.assertEqual(item["scheduled"], item["sent"] + item["skipped"])
                self.assertEqual(item["unexpected_results"], 0)
                self.assertEqual(item["transport_errors"], 0)
            self.assertGreater(phases[3]["http_or_business_errors"], 0)
            self.assertEqual(phases[4]["http_or_business_errors"], 0)
            self.assertGreater(phases[2]["skipped"], 0)
            self.assertEqual(Handler.active, 0)
            self.assertLessEqual(Handler.peak, 3)
            self.assertGreater(Handler.peak, 1)

    def test_unexpected_result_detected(self):
        # 强制失败却被适配器误报成功，应使结果不符合预期。
        with patch.object(traffic.project_adapter, "build_chat_request", side_effect=request), \
             patch.object(traffic.project_adapter, "response_is_success", return_value=True), \
             redirect_stdout(io.StringIO()):
            report = traffic.run_phase(self.base_url, traffic.Phase("errors", 20, 0.01, 2),
                                       0.2, 2, 2, threading.Event())
        self.assertGreater(report["unexpected_results"], 0)


if __name__ == "__main__":
    unittest.main()

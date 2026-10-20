"""Lab5 冒烟检查骨架：复制到个人实验仓库 scripts/smoke_test.py。

适配下方配置区后，在项目根目录执行 python scripts/smoke_test.py。
持久化应用通过 LAB5_DATA_DIR 读取测试数据目录，正常启动保持原配置。
"""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import ProxyHandler, Request, build_opener


# TODO：根据自己的应用确认这四项配置。
APP_IMPORT = "app:app"  # 工厂方式可用 "app:create_app()"
HOME_PATH = "/"
HELLO_PATH = "/api/hello"
EXPECTED_HELLO = {"message": "你好"}

# 以下流程已经提供，一般无需修改。
STARTUP_TIMEOUT = 20
REQUEST_TIMEOUT = 3
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def choose_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def wait_for_server(process, port):
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("应用在就绪前退出，请查看下方启动日志")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"等待应用就绪超过 {STARTUP_TIMEOUT} 秒")


def check_http(port):
    # 本机请求直接访问回环地址，不使用系统代理。
    opener = build_opener(ProxyHandler({}))
    for path, expected_type, expected_json in [
        (HOME_PATH, "text/html", None),
        (HELLO_PATH, "application/json", EXPECTED_HELLO),
    ]:
        request = Request(f"http://127.0.0.1:{port}{path}")
        with opener.open(request, timeout=REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8")
            if response.status != 200:
                raise RuntimeError(f"{path}: HTTP {response.status}")
            if response.headers.get_content_type() != expected_type:
                raise RuntimeError(f"{path}: 响应类型应为 {expected_type}")
            if expected_json is None:
                if "<html" not in body.lower():
                    raise RuntimeError(f"{path}: 未返回 HTML 页面")
            elif json.loads(body) != expected_json:
                raise RuntimeError(f"{path}: JSON 与 EXPECTED_HELLO 不一致")
        print(f"PASS {path}", flush=True)


def main():
    port = choose_port()
    with tempfile.TemporaryDirectory(prefix="lab5-smoke-") as data_dir:
        env = os.environ.copy()
        env.update(
            LAB5_DATA_DIR=data_dir,
            DEEPSEEK_API_KEY="lab5-test-placeholder",
            FLASK_SKIP_DOTENV="1",
            FLASK_DEBUG="0",
            PYTHONUNBUFFERED="1",
        )
        command = [
            sys.executable, "-m", "flask", "--app", APP_IMPORT, "run",
            "--host", "127.0.0.1", "--port", str(port),
            "--no-debugger", "--no-reload",
        ]
        with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as log:
            process = subprocess.Popen(
                command, cwd=PROJECT_ROOT, env=env,
                stdout=log, stderr=subprocess.STDOUT,
            )
            try:
                wait_for_server(process, port)
                print("服务已就绪", flush=True)
                check_http(port)
                if process.poll() is not None:
                    raise RuntimeError("检查期间应用退出")
            except Exception:
                log.seek(0)
                print("--- 应用启动日志 ---", file=sys.stderr)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                print("服务已停止", flush=True)
    print("冒烟检查通过", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"冒烟检查失败：{error}", file=sys.stderr)
        sys.exit(1)

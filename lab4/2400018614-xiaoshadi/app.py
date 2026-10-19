"""AI 聊天 Web 应用的后端服务。

同一个 Flask 服务同时承担两件事：

- 提供前端页面和静态资源（frontend/ 目录）
- 提供聊天记录的 RESTful API

聊天记录目前只保存在 Python 内存里，Flask 重启后会清空。
聊天回复有两种运行模式，由环境变量 CHAT_MODE 决定：

- mock（默认）：用本地模拟回复代替模型调用，不需要 DeepSeek Key，
  并开放实验用的模拟延迟与模拟失败选项，供 Lab 4 访问脚本制造变化；
- real：调用 DeepSeek API 生成真实回复，API Key 只从 .env 读取。

Lab 4 的监控指标定义在 metrics.py，/metrics 接口把聊天处理的累计次数、
在途请求数和服务端耗时交给 Prometheus 采集。
"""

import os
import threading
import time

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import CHAT_DURATION, CHAT_INPROGRESS, CHAT_REQUESTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# 从个人目录下的 .env 读取配置；文件不存在时不会报错，只是读不到变量
load_dotenv(os.path.join(BASE_DIR, ".env"))

# DeepSeek 官方 Chat Completions 接口（OpenAI 兼容格式）
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"

# 运行模式：mock 是本次实验的默认值，缺少 CHAT_MODE 时也按 mock 启动，
# 这样没有 Key 的机器也能完成 Lab 4。real 模式保留原来的真实模型调用。
CHAT_MODE = (os.getenv("CHAT_MODE") or "mock").strip().lower()
if CHAT_MODE not in ("mock", "real"):
    CHAT_MODE = "mock"
MOCK_MODE = CHAT_MODE == "mock"

# 当前配置下是否真的会访问外部模型，由状态接口如实报告
EXTERNAL_MODEL_CALLS = not MOCK_MODE

# mock 模式允许脚本请求的模拟等待上限（秒）：延迟由后端在处理期间真实发生，
# 但范围必须受限，避免这个实验接口被当成压测或滥用工具。
MAX_MOCK_DELAY_SECONDS = 5.0

MOCK_REPLY = "（本地模拟回复）已收到你的消息：{message}"

# static_url_path 设为空字符串，frontend/ 目录中的文件就直接挂在根路径下，
# 例如 /style.css 和 /app.js，前端页面里的相对引用因此可以直接命中。
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# 让 JSON 响应中的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False

# 聊天记录存放在内存中，Flask 重启后数据会丢失。
# 应用是单进程多线程的，实验脚本会并发发请求，所以用一把锁保护这个共享列表。
messages = []
messages_lock = threading.Lock()


@app.get("/")
def index():
    """返回前端页面。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/hello")
def hello():
    """最简单的连通性接口。"""
    return jsonify({"message": "你好"})


@app.get("/api/status")
def status():
    """实验用的状态接口：如实报告运行模式和是否调用外部模型。

    访问脚本先读这个接口，确认服务处于 mock 模式后才开始制造流量；
    这里返回的内容来自实际配置，不会在 real 模式下谎报成 mock。
    """
    return jsonify({"mode": CHAT_MODE, "external_model_calls": EXTERNAL_MODEL_CALLS})


@app.get("/metrics")
def metrics():
    """按 prometheus_client 标准格式返回当前指标，供 Prometheus 周期采集。

    这个接口本身属于监控通道，不计入聊天请求的数量和耗时。
    """
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------------------------
# 聊天记录的 CRUD 接口
#
# 一条聊天记录的数据结构约定为：
#     {"id": 1, "message": "用户输入", "reply": "后端回复"}
# ---------------------------------------------------------------------------


def _read_message_field(data):
    """从请求体里取出并校验 message 字段。

    返回 (message, error_response)，两者中只有一个不是 None。
    """
    if not isinstance(data, dict):
        return None, (jsonify({"error": "请求体必须是一个 JSON 对象"}), 400)

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, (jsonify({"error": "message 字段缺失，或内容为空"}), 400)

    return message.strip(), None


def _read_experiment_options(data):
    """读取实验脚本的模拟选项；只有 mock 模式才生效。

    - delay_seconds：让后端在本次处理中真实等待的秒数，超过上限会被截断；
    - force_error：让后端按脚本要求返回一次明确的模拟失败。

    real 模式一律返回 0/False，保证这些选项不会改变真实模型的调用行为。
    """
    if not MOCK_MODE or not isinstance(data, dict):
        return 0.0, False

    delay = data.get("delay_seconds", 0)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)) or delay < 0:
        delay = 0.0
    delay = min(float(delay), MAX_MOCK_DELAY_SECONDS)

    return delay, data.get("force_error") is True


def _next_id():
    """生成一个不与现有记录冲突的 id。调用方需持有 messages_lock。"""
    return max((record["id"] for record in messages), default=0) + 1


def _request_model_reply(message):
    """调用 DeepSeek API，返回模型生成的回复文本。

    Key 从环境变量读取，不会出现在代码或日志里；
    任何失败都抛出 RuntimeError，由调用方转成清晰的 JSON 错误。
    只有 real 模式会走到这里。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("后端没有读取到 DEEPSEEK_API_KEY，请检查个人目录下的 .env 文件")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"无法连接到 DeepSeek：{error}") from error

    if response.status_code != 200:
        detail = ""
        try:
            body = response.json()
            if isinstance(body, dict) and isinstance(body.get("error"), dict):
                detail = body["error"].get("message", "")
        except ValueError:
            detail = ""
        suffix = f"：{detail}" if detail else ""
        raise RuntimeError(f"DeepSeek 返回了错误状态 {response.status_code}{suffix}")

    try:
        reply = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError("无法从 DeepSeek 的响应中解析出回复内容") from error

    if not isinstance(reply, str) or not reply.strip():
        raise RuntimeError("DeepSeek 返回了空回复")

    return reply


def _run_chat(message, delay_seconds, force_error):
    """处理一次聊天请求，返回 (响应正文, HTTP 状态码)。

    这是原聊天处理流程的唯一入口：mock 模式用固定测试回复代替模型调用，
    real 模式仍然调用 DeepSeek；只有 mock 模式会执行模拟延迟与模拟失败。
    """
    if MOCK_MODE:
        if delay_seconds > 0:
            # 延迟真实发生在后端处理期间，不是客户端 sleep 冒充的
            time.sleep(delay_seconds)
        if force_error:
            return {"error": "模拟失败：后端按实验脚本要求拒绝了这次聊天请求"}, 503
        reply = MOCK_REPLY.format(message=message)
    else:
        try:
            reply = _request_model_reply(message)
        except RuntimeError as error:
            return {"error": str(error)}, 502

    with messages_lock:
        record = {"id": _next_id(), "message": message, "reply": reply}
        messages.append(record)

    return record, 201


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录并生成回复，整个处理过程记入监控指标。"""
    payload = request.get_json(silent=True)
    message, error = _read_message_field(payload)
    if error:
        # 请求正文不合法，还没进入聊天处理，不计入聊天指标
        return error

    delay_seconds, force_error = _read_experiment_options(payload)

    CHAT_INPROGRESS.inc()
    started = time.perf_counter()
    outcome = "error"  # 处理过程中抛异常时也按失败收尾
    try:
        body, status_code = _run_chat(message, delay_seconds, force_error)
        outcome = "success" if status_code < 400 else "error"
        return jsonify(body), status_code
    finally:
        # 无论成功、模拟失败还是异常，三件收尾动作都要执行：
        # 在途数回落、耗时被记录、按结果累计一次
        CHAT_INPROGRESS.dec()
        CHAT_DURATION.observe(time.perf_counter() - started)
        CHAT_REQUESTS.labels(outcome=outcome).inc()


@app.get("/api/messages")
def list_messages():
    """读取全部聊天记录。"""
    with messages_lock:
        return jsonify(list(messages))


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定 id 的聊天记录。"""
    message, error = _read_message_field(request.get_json(silent=True))
    if error:
        return error

    with messages_lock:
        for record in messages:
            if record["id"] == message_id:
                record["message"] = message
                return jsonify(record)

    return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定 id 的聊天记录。"""
    with messages_lock:
        for index, record in enumerate(messages):
            if record["id"] == message_id:
                messages.pop(index)
                return jsonify({"id": message_id, "deleted": True})

    return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404


if __name__ == "__main__":
    # 本地实验：单进程多线程，处理慢请求时 /metrics 仍能响应；
    # debug 关闭以免重载器产生第二个进程、造成指标重复或丢失。
    app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)

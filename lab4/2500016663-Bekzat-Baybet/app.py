"""AI 聊天助手后端服务（Lab 4：加入监控指标）。

同一个 Flask 进程同时提供：
- 前端页面（frontend/ 目录下的静态文件）
- 聊天记录 CRUD API（回复由模型生成）
- 监控指标：/metrics 供 Prometheus 采集，/api/status 供实验脚本核验模式

回复来源由环境变量 CHAT_MODE 决定：
- mock（默认）：返回固定测试回复，可模拟后端延迟与失败，不需要 API Key
- real：沿用原来的 DeepSeek 调用，本次实验不运行

数据只保存在内存列表中，Flask 重启后清空（本阶段刻意不持久化）。
API Key 通过 .env 提供，只存在于后端进程的环境中；mock 模式不读取它也不需要它。
"""

import math
import os
import threading
import time

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

import metrics

# 从项目根目录的 .env 文件加载环境变量（文件不存在时静默跳过）
load_dotenv()

app = Flask(__name__)

# 让 JSON 响应中的中文直接显示，而不是被转义成 \uXXXX
app.json.ensure_ascii = False

# ---------- 运行模式 ----------

# 默认 mock：没有 Key 也能启动，并且不会进入真实模型调用。
CHAT_MODE = os.getenv("CHAT_MODE", "mock").strip().lower()
if CHAT_MODE not in ("mock", "real"):
    raise RuntimeError("CHAT_MODE 只能是 mock 或 real")
MOCK_MODE = CHAT_MODE == "mock"

# mock 模式下允许的最大实验延迟（秒），避免异常大的数值把请求挂死。
MAX_MOCK_DELAY_SECONDS = 10.0

# mock 模式的固定测试回复，不含任何真实模型输出。
MOCK_REPLY = "这是一条模拟回复：本次监控实验使用本地固定文本，不调用真实模型。"

# DeepSeek 官方 API 配置（文档：https://api-docs.deepseek.com/zh-cn/）
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 内存中的聊天记录：每个元素形如 {"id": 1, "message": "用户输入", "reply": "模型回复"}
messages = []
# 自增 id 计数器，用于保证每条记录的 id 唯一
next_id = 1
# 应用是多线程的，用一把锁保护上面的记录列表与 id 计数器
messages_lock = threading.Lock()


class MockModelError(Exception):
    """mock 模式下由实验选项 force_error 触发的模拟失败。"""


# ---------- 前端页面路由 ----------


@app.route("/")
def serve_index():
    """访问 http://localhost:5001/ 时返回前端页面。"""
    return send_from_directory("frontend", "index.html")


@app.route("/<path:filename>")
def serve_frontend_file(filename):
    """提供 frontend/ 下的其他静态文件（style.css、app.js 等）。

    Flask 会优先匹配更具体的路由（例如 /api/messages/<id>），
    只有匹配不上的路径才会落到这里。
    """
    return send_from_directory("frontend", filename)


# ---------- DeepSeek 调用 ----------


def call_deepseek(message):
    """把用户消息发给 DeepSeek，返回模型回复文本；失败时抛出异常。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # 只判断变量是否存在，绝不输出它的值
        raise ValueError("服务器缺少 DEEPSEEK_API_KEY，请检查 .env 是否创建")

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": message}],
        },
        timeout=30,
    )
    # 4xx / 5xx 响应时抛出 requests.HTTPError
    response.raise_for_status()
    data = response.json()
    # 官方响应结构：choices[0].message.content 即模型回复文本
    return data["choices"][0]["message"]["content"]


def normalize_mock_delay(value):
    """把实验延迟限制在合法范围内，非法或越界的数值按边界处理。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        return 0.0
    return min(seconds, MAX_MOCK_DELAY_SECONDS)


def call_model(message, delay_seconds=0, force_error=False):
    """按当前模式取得回复。

    mock 模式：延迟由后端在本次处理期间真实消耗，force_error 触发模拟失败。
    这两个选项只在 mock 模式生效，不会改变 real 模式的真实调用行为。
    """
    if not MOCK_MODE:
        return call_deepseek(message)

    delay = normalize_mock_delay(delay_seconds)
    if delay > 0:
        time.sleep(delay)
    if force_error:
        raise MockModelError("模拟的外部模型调用失败")
    return MOCK_REPLY


# ---------- 监控指标端点 ----------


@app.route("/metrics")
def expose_metrics():
    """供 Prometheus 采集的指标端点。

    这个端点自身、/api/status 以及前端静态资源都不计入聊天指标。
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api/status")
def experiment_status():
    """实验状态接口：如实反映当前模式，供访问脚本核验。

    real 模式下不会报告 mock，避免脚本在真实模型上误发请求。
    """
    return jsonify({
        "mode": CHAT_MODE,
        "external_model_calls": not MOCK_MODE,
    })


# ---------- API ----------


@app.route("/api/hello")
def hello():
    """健康检查接口。"""
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    """创建一条聊天记录：读取 message，reply 由模型生成。

    整段处理计入聊天指标：开始处理时在途数加一，结束时无论成功、模拟失败
    还是异常，都记录耗时并把在途数减一。
    """
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "字段 message 不能为空"}), 400

    # 实验选项：只在 mock 模式生效，real 模式下被忽略
    delay_seconds = data.get("delay_seconds", 0)
    force_error = bool(data.get("force_error", False))

    metrics.CHAT_INPROGRESS.inc()
    started = time.perf_counter()
    outcome = "error"
    try:
        # 先拿到模型回复，调用成功后才保存记录
        reply = call_model(message.strip(), delay_seconds, force_error)

        with messages_lock:
            record = {
                "id": next_id,
                "message": message.strip(),
                "reply": reply,
            }
            next_id += 1
            messages.append(record)

        outcome = "success"
        # 201 Created：表示资源创建成功
        return jsonify(record), 201
    except MockModelError as exc:
        # 脚本要求的模拟失败，返回明确的错误响应
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        # Key 缺失属于服务器配置错误
        return jsonify({"error": str(exc)}), 500
    except requests.RequestException as exc:
        # 网络错误、超时、DeepSeek 返回 4xx/5xx
        return jsonify({"error": f"调用 DeepSeek API 失败：{exc}"}), 502
    except (KeyError, IndexError):
        # 响应 JSON 结构不符合预期
        return jsonify({"error": "DeepSeek 返回了无法解析的响应"}), 502
    finally:
        # 异常路径也必须如实收尾，指标不能只记成功
        metrics.CHAT_DURATION.observe(time.perf_counter() - started)
        metrics.CHAT_REQUESTS.labels(outcome=outcome).inc()
        metrics.CHAT_INPROGRESS.dec()


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """返回全部聊天记录。"""
    with messages_lock:
        snapshot = list(messages)
    return jsonify(snapshot)


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    """修改指定 id 记录的 message 字段。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "字段 message 不能为空"}), 400

    with messages_lock:
        for record in messages:
            if record["id"] == message_id:
                record["message"] = message.strip()
                return jsonify(record)

    return jsonify({"error": f"id 为 {message_id} 的记录不存在"}), 404


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """删除指定 id 的记录。"""
    with messages_lock:
        for index, record in enumerate(messages):
            if record["id"] == message_id:
                messages.pop(index)
                # 204 No Content：表示删除成功，响应没有正文
                return "", 204

    return jsonify({"error": f"id 为 {message_id} 的记录不存在"}), 404


if __name__ == "__main__":
    # 单进程 + 多线程：慢聊天请求处理期间 /metrics 仍能被采集到；
    # 刻意不开 debug 重载器，避免起两个进程导致指标被重复注册。
    app.run(host="127.0.0.1", port=5001, threaded=True)

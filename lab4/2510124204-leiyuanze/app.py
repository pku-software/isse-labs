import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.request

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

import metrics


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
ENV_FILE = Path(__file__).resolve().parent / ".env"
DATA_DIR = Path(__file__).resolve().parent / "data"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
MAX_DELAY_SECONDS = 10.0

load_dotenv(ENV_FILE)

app = Flask(__name__)
app.json.ensure_ascii = False

# Lab 4：默认本地模拟模式，不调用外部模型、不需要 API Key；
# 设置 CHAT_MODE=real 才走原来的 DeepSeek 调用。
CHAT_MODE = os.getenv("CHAT_MODE", "mock").strip().lower()
IS_MOCK_MODE = CHAT_MODE == "mock"
external_model_calls_enabled = not IS_MOCK_MODE

# 教学用最小线程安全：聊天请求会并发写入共享的 conversations 列表。
conversations_lock = threading.Lock()


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_conversations():
    if not CONVERSATIONS_FILE.exists():
        return []

    try:
        payload = json.loads(CONVERSATIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        app.logger.error("Could not load conversations: %s", type(error).__name__)
        return []

    if not isinstance(payload, list):
        app.logger.error("conversations.json must contain a JSON array")
        return []

    records = []
    for conversation in payload:
        if not isinstance(conversation, dict):
            continue

        conversation_id = conversation.get("id")
        title = conversation.get("title")
        created_at = conversation.get("createdAt")
        updated_at = conversation.get("updatedAt")
        raw_messages = conversation.get("messages")

        if (
            not isinstance(conversation_id, int)
            or not isinstance(title, str)
            or not isinstance(created_at, str)
            or not isinstance(updated_at, str)
            or not isinstance(raw_messages, list)
        ):
            continue

        records.append(
            {
                "id": conversation_id,
                "title": title,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "messages": [
                    message
                    for message in raw_messages
                    if isinstance(message, dict)
                    and isinstance(message.get("id"), int)
                    and isinstance(message.get("message"), str)
                    and isinstance(message.get("reply"), str)
                    and isinstance(message.get("createdAt"), str)
                ],
            }
        )

    return records


def save_conversations():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_file = CONVERSATIONS_FILE.with_suffix(".json.tmp")
    temporary_file.write_text(
        json.dumps(conversations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_file.replace(CONVERSATIONS_FILE)


def find_conversation(conversation_id):
    return next(
        (
            conversation
            for conversation in conversations
            if conversation["id"] == conversation_id
        ),
        None,
    )


def find_message(conversation, message_id):
    return next(
        (
            message
            for message in conversation["messages"]
            if message["id"] == message_id
        ),
        None,
    )


def parse_message_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 不能为空"

    return message.strip(), None


def parse_title_payload():
    data = request.get_json(silent=True)
    if data is None:
        return None, None
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    title = data.get("title")
    if title is None:
        return None, None
    if not isinstance(title, str) or not title.strip():
        return None, "title 不能为空"
    if len(title.strip()) > 80:
        return None, "title 不能超过 80 个字符"

    return title.strip(), None


def parse_experiment_payload(data):
    """解析只在 mock 模式生效的实验选项：delay_seconds、force_error。

    返回 (delay_seconds, force_error, error)；real 模式忽略这两个选项。
    延迟限制在 0 到 MAX_DELAY_SECONDS 秒之间，范围外的请求按无效参数处理。
    """
    if not IS_MOCK_MODE or not isinstance(data, dict):
        return 0.0, False, None

    delay = data.get("delay_seconds", 0)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)):
        return 0.0, False, "delay_seconds 必须是数字"
    if not 0 <= float(delay) <= MAX_DELAY_SECONDS:
        return 0.0, False, f"delay_seconds 必须在 0 到 {MAX_DELAY_SECONDS:g} 之间"

    force_error = data.get("force_error", False)
    if not isinstance(force_error, bool):
        return 0.0, False, "force_error 必须是布尔值"

    return float(delay), force_error, None


def conversation_summary(conversation):
    last_message = conversation["messages"][-1]["message"] if conversation["messages"] else None
    return {
        "id": conversation["id"],
        "title": conversation["title"],
        "messageCount": len(conversation["messages"]),
        "lastMessage": last_message,
        "createdAt": conversation["createdAt"],
        "updatedAt": conversation["updatedAt"],
    }


def mock_reply(message, delay_seconds):
    """本地模拟回复：不调用任何外部模型，只用于 Lab 4 监控实验。"""
    if delay_seconds > 0:
        return (
            "【本地模拟回复】这是 Lab 4 监控实验的固定测试回复，"
            f"本次请求在后端等待了 {delay_seconds:g} 秒。"
        )
    return "【本地模拟回复】这是 Lab 4 监控实验的固定测试回复。"


def generate_reply(message, history, delay_seconds=0.0, force_error=False):
    if IS_MOCK_MODE:
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        if force_error:
            return None, ("模拟的模型调用失败", 503)
        return mock_reply(message, delay_seconds), None

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ("DEEPSEEK_API_KEY 未配置", 503)

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    model_messages = []
    for previous_message in history[-10:]:
        model_messages.append(
            {"role": "user", "content": previous_message["message"]}
        )
        model_messages.append(
            {"role": "assistant", "content": previous_message["reply"]}
        )
    model_messages.append({"role": "user", "content": message})

    payload = {
        "model": model,
        "messages": model_messages,
        "stream": False,
        "thinking": {"type": "disabled"},
    }
    api_request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(api_request, timeout=60) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        app.logger.error("DeepSeek HTTP error: %s", error.code)
        return None, ("DeepSeek 服务暂时不可用，请稍后重试", 502)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        app.logger.error("DeepSeek request failed: %s", type(error).__name__)
        return None, ("DeepSeek 服务暂时不可用，请稍后重试", 502)

    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        return None, ("DeepSeek 没有返回可用回复", 502)

    reply = choices[0].get("message", {}).get("content")
    if not isinstance(reply, str) or not reply.strip():
        return None, ("DeepSeek 没有返回可用回复", 502)

    return reply.strip(), None


def record_chat_outcome(success, started):
    """聊天处理结束后记录一次耗时与结果；无论成功失败都调用。"""
    metrics.CHAT_REQUEST_DURATION.observe(time.monotonic() - started)
    metrics.CHAT_REQUESTS.labels(outcome="success" if success else "error").inc()


conversations = load_conversations()
if not conversations:
    # 保证全新环境也有一个可用会话，供访问脚本的固定接口使用。
    _now = utc_now()
    conversations.append(
        {
            "id": 1,
            "title": "Lab4 监控实验",
            "createdAt": _now,
            "updatedAt": _now,
            "messages": [],
        }
    )
    save_conversations()
next_conversation_id = max(
    (conversation["id"] for conversation in conversations),
    default=0,
) + 1
next_message_id = max(
    (
        message["id"]
        for conversation in conversations
        for message in conversation["messages"]
    ),
    default=0,
) + 1


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def javascript():
    return send_from_directory(FRONTEND_DIR, "app.js")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/status")
def status():
    """Lab 4：供访问脚本通过真实 HTTP 核验当前运行模式。"""
    return jsonify(
        {
            "mode": CHAT_MODE,
            "external_model_calls": external_model_calls_enabled,
        }
    )


@app.get("/metrics")
def prometheus_metrics():
    # 业务指标只在聊天处理流程中记录；这里仅按标准格式返回当前指标文本。
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get("/api/conversations")
def list_conversations():
    summaries = [conversation_summary(item) for item in conversations]
    summaries.sort(key=lambda item: item["updatedAt"], reverse=True)
    return jsonify(summaries)


@app.post("/api/conversations")
def create_conversation():
    global next_conversation_id

    title, error = parse_title_payload()
    if error:
        return jsonify({"error": error}), 400

    with conversations_lock:
        now = utc_now()
        conversation = {
            "id": next_conversation_id,
            "title": title or f"新会话 {next_conversation_id}",
            "createdAt": now,
            "updatedAt": now,
            "messages": [],
        }
        next_conversation_id += 1
        conversations.append(conversation)

        try:
            save_conversations()
        except OSError as error:
            conversations.remove(conversation)
            next_conversation_id -= 1
            app.logger.error(
                "Could not save created conversation: %s",
                type(error).__name__,
            )
            return jsonify({"error": "会话保存失败"}), 500

    return jsonify(conversation), 201


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def rename_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    title, error = parse_title_payload()
    if error:
        return jsonify({"error": error}), 400
    if title is None:
        return jsonify({"error": "title 不能为空"}), 400

    with conversations_lock:
        previous_title = conversation["title"]
        previous_updated_at = conversation["updatedAt"]
        conversation["title"] = title
        conversation["updatedAt"] = utc_now()

        try:
            save_conversations()
        except OSError as error:
            conversation["title"] = previous_title
            conversation["updatedAt"] = previous_updated_at
            app.logger.error(
                "Could not save renamed conversation: %s",
                type(error).__name__,
            )
            return jsonify({"error": "会话保存失败"}), 500

    return jsonify(conversation_summary(conversation))


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    with conversations_lock:
        conversation_index = conversations.index(conversation)
        conversations.remove(conversation)

        try:
            save_conversations()
        except OSError as error:
            conversations.insert(conversation_index, conversation)
            app.logger.error(
                "Could not save deleted conversation: %s",
                type(error).__name__,
            )
            return jsonify({"error": "会话保存失败"}), 500

    return jsonify({"deleted": conversation_id})


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_message(conversation_id):
    global next_message_id

    data = request.get_json(silent=True)
    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    delay_seconds, force_error, error = parse_experiment_payload(data)
    if error:
        return jsonify({"error": error}), 400

    # Lab 4：只统计聊天处理；开始处理加一，处理结束（无论成败）减一。
    metrics.CHAT_INPROGRESS.inc()
    started = time.monotonic()
    try:
        with conversations_lock:
            conversation = find_conversation(conversation_id)
            if conversation is None:
                record_chat_outcome(False, started)
                return jsonify({"error": "会话不存在"}), 404
            history = list(conversation["messages"])

        reply, api_error = generate_reply(message, history, delay_seconds, force_error)
        if api_error:
            detail, status_code = api_error
            record_chat_outcome(False, started)
            return jsonify({"error": detail}), status_code

        with conversations_lock:
            if find_conversation(conversation_id) is None:
                record_chat_outcome(False, started)
                return jsonify({"error": "会话不存在"}), 404

            record = {
                "id": next_message_id,
                "message": message,
                "reply": reply,
                "createdAt": utc_now(),
            }
            previous_updated_at = conversation["updatedAt"]
            next_message_id += 1
            conversation["messages"].append(record)
            conversation["updatedAt"] = record["createdAt"]

            try:
                save_conversations()
            except OSError as error:
                conversation["messages"].remove(record)
                conversation["updatedAt"] = previous_updated_at
                next_message_id -= 1
                app.logger.error("Could not save created message: %s", type(error).__name__)
                record_chat_outcome(False, started)
                return jsonify({"error": "聊天记录保存失败"}), 500

        record_chat_outcome(True, started)
        return jsonify(record), 201
    except Exception:
        record_chat_outcome(False, started)
        app.logger.exception("Unexpected error while handling chat request")
        return jsonify({"error": "聊天处理失败"}), 500
    finally:
        metrics.CHAT_INPROGRESS.dec()


@app.patch("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def update_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    record = find_message(conversation, message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    with conversations_lock:
        previous_message = record["message"]
        previous_updated_at = conversation["updatedAt"]
        record["message"] = message
        conversation["updatedAt"] = utc_now()

        try:
            save_conversations()
        except OSError as error:
            record["message"] = previous_message
            conversation["updatedAt"] = previous_updated_at
            app.logger.error("Could not save updated message: %s", type(error).__name__)
            return jsonify({"error": "聊天记录保存失败"}), 500

    return jsonify(record)


@app.delete("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def delete_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    record = find_message(conversation, message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    with conversations_lock:
        record_index = conversation["messages"].index(record)
        previous_updated_at = conversation["updatedAt"]
        conversation["messages"].remove(record)
        conversation["updatedAt"] = utc_now()

        try:
            save_conversations()
        except OSError as error:
            conversation["messages"].insert(record_index, record)
            conversation["updatedAt"] = previous_updated_at
            app.logger.error("Could not save deleted message: %s", type(error).__name__)
            return jsonify({"error": "聊天记录保存失败"}), 500

    return jsonify({"deleted": message_id})


if __name__ == "__main__":
    # threaded=True：慢聊天期间 /metrics 仍能响应；debug=False 避免重复进程与指标翻倍。
    app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)
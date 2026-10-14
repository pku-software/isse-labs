import json
import math
import os
from pathlib import Path
import threading
import time

from flask import Flask, abort, jsonify, render_template, request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import track_chat_request


APP_MODE = os.getenv("CHAT_APP_MODE", "mock").strip().lower()
if APP_MODE not in {"mock", "real"}:
    raise RuntimeError("CHAT_APP_MODE 必须为 mock 或 real。")

# 只有真实模式才加载本地 .env；默认实验模式不会读取密钥文件。
if APP_MODE == "real":
    from dotenv import load_dotenv

    load_dotenv()

LAB4_EXPERIMENT_ENABLED = os.getenv("LAB4_EXPERIMENT_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
}

app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="frontend",
    static_url_path="/static",
)
app.json.ensure_ascii = False

DATA_FILE = Path(
    os.getenv(
        "CHAT_DATA_FILE",
        str(Path(__file__).resolve().parent / ".runtime" / "app" / "messages.json"),
    )
)
messages_lock = threading.RLock()


def load_messages():
    if not DATA_FILE.exists():
        return []
    content = DATA_FILE.read_text(encoding="utf-8")
    if not content.strip():
        return []
    try:
        stored_messages = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError("聊天记录文件不是有效的 JSON 文件。") from error
    if not isinstance(stored_messages, list) or any(
        not isinstance(item, dict) for item in stored_messages
    ):
        raise RuntimeError("聊天记录文件应为聊天记录对象组成的数组。")
    return stored_messages


messages = load_messages()
existing_ids = [
    item["id"]
    for item in messages
    if isinstance(item.get("id"), int) and not isinstance(item.get("id"), bool)
]
next_message_id = max(existing_ids, default=0) + 1


def save_messages():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_name(f"{DATA_FILE.name}.tmp")
    serialized = json.dumps(messages, ensure_ascii=False, indent=2) + "\n"
    temporary_file.write_text(serialized, encoding="utf-8")
    temporary_file.replace(DATA_FILE)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/lab4/status")
def lab4_status():
    if not LAB4_EXPERIMENT_ENABLED:
        abort(404)
    return jsonify(
        {
            "mode": APP_MODE,
            "external_model_calls": APP_MODE == "real",
        }
    )


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )


def ask_deepseek(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, (jsonify({"error": "服务端尚未配置 DEEPSEEK_API_KEY。"}), 503)

    import requests

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-flash",
                "messages": [{"role": "user", "content": message}],
                "stream": False,
            },
            timeout=60,
        )
    except requests.Timeout:
        return None, (jsonify({"error": "DeepSeek 请求超时，请稍后重试。"}), 502)
    except requests.RequestException:
        return None, (jsonify({"error": "无法连接 DeepSeek API，请稍后重试。"}), 502)

    if response.status_code == 401:
        return None, (jsonify({"error": "DeepSeek API 鉴权失败，请检查服务端配置。"}), 502)
    if not response.ok:
        return None, (
            jsonify({"error": f"DeepSeek API 返回错误（HTTP {response.status_code}）。"}),
            502,
        )

    try:
        payload = response.json()
        reply = payload["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        return None, (jsonify({"error": "DeepSeek API 返回了无法识别的响应。"}), 502)

    if not isinstance(reply, str) or not reply.strip():
        return None, (jsonify({"error": "DeepSeek API 没有返回有效文本。"}), 502)
    return reply.strip(), None


def experiment_options(data):
    """Validate request-controlled delay and failure before applying either option."""
    delay = data.get("lab4_delay_seconds", 0.0)
    force_error = data.get("lab4_force_error", False)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)):
        return None, None, (jsonify({"error": "模拟延迟必须是数字。"}), 400)
    if not math.isfinite(delay) or not 0 <= delay <= 5:
        return None, None, (jsonify({"error": "模拟延迟范围为 0 到 5 秒。"}), 400)
    if not isinstance(force_error, bool):
        return None, None, (jsonify({"error": "模拟失败选项必须是布尔值。"}), 400)
    return float(delay), force_error, None


@app.post("/api/messages")
@track_chat_request
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求内容必须是 JSON 对象。"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空，且必须是文本。"}), 400
    clean_message = message.strip()

    if APP_MODE == "mock":
        delay_seconds = 0.0
        force_error = False
        if LAB4_EXPERIMENT_ENABLED:
            delay_seconds, force_error, option_error = experiment_options(data)
            if option_error is not None:
                return option_error
            if delay_seconds:
                time.sleep(delay_seconds)
            if force_error:
                return jsonify({"error": "这是监控实验触发的模拟错误。"}), 503
        reply = "这是本地模拟回复；本次请求没有调用外部模型。"
    else:
        # Real mode retains the original DeepSeek behavior and ignores Lab 4 options.
        reply, error_response = ask_deepseek(clean_message)
        if error_response is not None:
            return error_response

    with messages_lock:
        record = {
            "id": next_message_id,
            "message": clean_message,
            "reply": reply,
        }
        messages.append(record)
        try:
            save_messages()
        except OSError:
            messages.pop()
            return jsonify({"error": "聊天记录写入文件失败，请检查文件权限。"}), 500
        next_message_id += 1

    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        snapshot = [dict(item) for item in messages]
    return jsonify({"messages": snapshot})


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求内容必须是 JSON 对象。"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空，且必须是文本。"}), 400

    with messages_lock:
        record = next((item for item in messages if item["id"] == message_id), None)
        if record is None:
            return jsonify({"error": "聊天记录不存在。"}), 404

        old_message = record["message"]
        record["message"] = message.strip()
        try:
            save_messages()
        except OSError:
            record["message"] = old_message
            return jsonify({"error": "聊天记录写入文件失败，请检查文件权限。"}), 500
        return jsonify(dict(record))


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        index = next(
            (i for i, item in enumerate(messages) if item["id"] == message_id),
            None,
        )
        if index is None:
            return jsonify({"error": "聊天记录不存在。"}), 404

        deleted = messages.pop(index)
        try:
            save_messages()
        except OSError:
            messages.insert(index, deleted)
            return jsonify({"error": "聊天记录写入文件失败，请检查文件权限。"}), 500
        return jsonify({"message": "聊天记录已删除。", "id": deleted["id"]})


if __name__ == "__main__":
    app.run(
        host=os.getenv("CHAT_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5001")),
        threaded=True,
        debug=False,
        use_reloader=False,
    )

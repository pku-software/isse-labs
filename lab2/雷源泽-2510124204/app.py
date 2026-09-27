import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
ENV_FILE = Path(__file__).resolve().parent / ".env"

load_dotenv(ENV_FILE)

app = Flask(__name__)
app.json.ensure_ascii = False

messages = []
next_message_id = 1


def find_message(message_id):
    return next(
        (message for message in messages if message["id"] == message_id),
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


def generate_reply(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ("DEEPSEEK_API_KEY 未配置", 503)

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
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


@app.post("/api/messages")
def create_message():
    global next_message_id

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    reply, api_error = generate_reply(message)
    if api_error:
        detail, status_code = api_error
        return jsonify({"error": detail}), status_code

    record = {
        "id": next_message_id,
        "message": message,
        "reply": reply,
    }
    next_message_id += 1
    messages.append(record)

    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"deleted": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

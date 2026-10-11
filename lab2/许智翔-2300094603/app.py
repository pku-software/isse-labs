import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

DATA_FILE = Path(__file__).resolve().parent / "data" / "messages.json"


def load_messages():
    if not DATA_FILE.exists():
        return []
    content = DATA_FILE.read_text(encoding="utf-8")
    if not content.strip():
        return []
    try:
        stored_messages = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError("data/messages.json 不是有效的 JSON 文件。") from error
    if not isinstance(stored_messages, list) or any(not isinstance(item, dict) for item in stored_messages):
        raise RuntimeError("data/messages.json 的格式应为聊天记录对象组成的数组。")
    return stored_messages


# 启动时从 JSON 文件恢复；文件不存在或为空时从空列表开始。
messages = load_messages()
existing_ids = [
    item["id"]
    for item in messages
    if isinstance(item.get("id"), int) and not isinstance(item.get("id"), bool)
]
next_message_id = max(existing_ids, default=0) + 1


def save_messages():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".tmp")
    serialized = json.dumps(messages, ensure_ascii=False, indent=2) + "\n"
    temporary_file.write_text(serialized, encoding="utf-8")
    temporary_file.replace(DATA_FILE)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


def ask_deepseek(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, (jsonify({"error": "服务端尚未配置 DEEPSEEK_API_KEY。"}), 503)

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
        return None, (jsonify({"error": "无法连接 DeepSeek API，请检查网络后重试。"}), 502)

    if response.status_code == 401:
        return None, (jsonify({"error": "DeepSeek API 鉴权失败，请检查本地密钥配置。"}), 502)
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


@app.post("/api/messages")
def create_message():
    global next_message_id
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求内容必须是 JSON 对象。"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空，且必须是文本。"}), 400

    clean_message = message.strip()
    reply, error_response = ask_deepseek(clean_message)
    if error_response is not None:
        return error_response

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
    return jsonify({"messages": messages})


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求内容必须是 JSON 对象。"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空，且必须是文本。"}), 400

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
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    index = next((i for i, item in enumerate(messages) if item["id"] == message_id), None)
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
    app.run(port=5001, debug=True)

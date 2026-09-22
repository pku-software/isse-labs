import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI


load_dotenv()


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

BASE_DIR = Path(__file__).resolve().parent
MESSAGES_FILE = BASE_DIR / "data" / "messages.json"


def load_messages():
    if not MESSAGES_FILE.exists():
        return []

    content = MESSAGES_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        app.logger.warning("messages.json is invalid; starting with empty data")
        return []

    if not isinstance(data, list):
        app.logger.warning("messages.json must contain a list; starting with empty data")
        return []

    return data


def save_messages():
    MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    MESSAGES_FILE.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


messages = load_messages()
next_message_id = max(
    (item.get("id", 0) for item in messages if isinstance(item, dict)),
    default=0,
) + 1


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


def read_message_from_request():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请提供 JSON 格式的请求体"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 必须是非空字符串"

    return message.strip(), None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    message, error = read_message_from_request()
    if error:
        return jsonify({"error": error}), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务器缺少 DeepSeek API Key 配置"}), 503

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message}],
            stream=False,
        )
        reply = completion.choices[0].message.content
        if not reply:
            raise ValueError("DeepSeek returned an empty reply")
    except Exception:
        app.logger.error("DeepSeek API call failed")
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    record = {"id": next_message_id, "message": message, "reply": reply}
    messages.append(record)
    next_message_id += 1
    save_messages()
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = read_message_from_request()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = message
    save_messages()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    save_messages()
    return jsonify({"message": "聊天记录已删除"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

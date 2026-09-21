import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI


load_dotenv()


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

DATA_FILE = Path(__file__).resolve().parent / "data" / "messages.json"


def load_messages():
    if not DATA_FILE.exists():
        return []

    content = DATA_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return []

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("messages.json 的最外层必须是数组")
    return data


def save_messages():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


messages = load_messages()
next_message_id = max(
    (item.get("id", 0) for item in messages if isinstance(item, dict)),
    default=0,
) + 1


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 请求体"}), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify({"error": "message 不能为空"}), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message_text.strip()}],
            stream=False,
        )
        reply = response.choices[0].message.content
        if not reply:
            raise ValueError("DeepSeek returned an empty reply")
    except Exception:
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    message = {
        "id": next_message_id,
        "message": message_text.strip(),
        "reply": reply,
    }
    messages.append(message)
    next_message_id += 1
    save_messages()
    return jsonify(message), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    message = find_message(message_id)
    if message is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 请求体"}), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify({"error": "message 不能为空"}), 400

    message["message"] = message_text.strip()
    save_messages()
    return jsonify(message)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    message = find_message(message_id)
    if message is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(message)
    save_messages()
    return jsonify({"message": "删除成功"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

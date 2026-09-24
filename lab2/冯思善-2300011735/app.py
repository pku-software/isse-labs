import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI


load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-flash"

messages = []
next_message_id = 1


def find_message(message_id):
    return next(
        (message for message in messages if message["id"] == message_id),
        None,
    )


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
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务器未配置 DEEPSEEK_API_KEY"}), 503

    try:
        client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
        completion = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": message_text.strip()}],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )
        reply = completion.choices[0].message.content
        if not isinstance(reply, str) or not reply.strip():
            raise ValueError("DeepSeek returned an empty reply")
    except Exception as error:
        app.logger.error("DeepSeek API call failed: %s", type(error).__name__)
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    message = {
        "id": next_message_id,
        "message": message_text.strip(),
        "reply": reply.strip(),
    }
    messages.append(message)
    next_message_id += 1

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
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    message["message"] = message_text.strip()
    return jsonify(message)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    message = find_message(message_id)
    if message is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(message)
    return jsonify({"id": message_id, "message": "删除成功"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

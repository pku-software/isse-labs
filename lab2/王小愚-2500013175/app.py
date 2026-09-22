import os

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

messages = []
next_message_id = 1


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=60.0,
        )
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message.strip()}],
            stream=False,
        )
        reply = completion.choices[0].message.content
        if not reply:
            raise ValueError("DeepSeek returned an empty reply")
    except Exception:
        app.logger.exception("DeepSeek API request failed")
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    record = {
        "id": next_message_id,
        "message": message.strip(),
        "reply": reply,
    }
    messages.append(record)
    next_message_id += 1
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    record["message"] = message.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"message": "聊天记录已删除"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

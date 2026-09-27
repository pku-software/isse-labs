import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

# 当前阶段只保存在 Flask 进程内存中，重启后记录会清空。
messages = []
next_message_id = 1


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
    next_message_id += 1
    messages.append(record)
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

    record["message"] = message.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    index = next((i for i, item in enumerate(messages) if item["id"] == message_id), None)
    if index is None:
        return jsonify({"error": "聊天记录不存在。"}), 404

    deleted = messages.pop(index)
    return jsonify({"message": "聊天记录已删除。", "id": deleted["id"]})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

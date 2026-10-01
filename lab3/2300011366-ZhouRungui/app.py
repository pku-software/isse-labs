import os
from itertools import count

import requests
from flask import Flask, jsonify, request, send_from_directory


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
messages = []
message_ids = count(1)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    data = request.get_json(silent=True)
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务器尚未配置 DeepSeek API Key"}), 503

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            json={
                "model": "deepseek-flash",
                "messages": [{"role": "user", "content": message.strip()}],
                "thinking": {"type": "disabled"},
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.HTTPError:
        return jsonify({"error": "DeepSeek API 请求失败，请检查 Key 或稍后重试"}), 502
    except requests.RequestException:
        return jsonify({"error": "暂时无法连接 DeepSeek API，请稍后重试"}), 502

    try:
        result = response.json()
    except ValueError:
        return jsonify({"error": "DeepSeek API 返回了非 JSON 数据"}), 502

    if not isinstance(result, dict):
        return jsonify({"error": "DeepSeek API 返回的 JSON 格式不正确"}), 502
    if "error" in result:
        return jsonify({"error": "DeepSeek API 返回了错误信息，请检查账号和 Key 状态"}), 502

    choices = result.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return jsonify({"error": "DeepSeek API 回复中缺少 choices"}), 502

    choice = choices[0]
    model_message = choice.get("message")
    if not isinstance(model_message, dict):
        return jsonify({"error": "DeepSeek API 回复中缺少 message"}), 502

    reply = model_message.get("content")
    if not isinstance(reply, str) or not reply.strip():
        reason = choice.get("finish_reason")
        if reason in {"length", "content_filter", "insufficient_system_resource", "aborted"}:
            return jsonify({"error": f"DeepSeek 未生成文本，结束原因：{reason}"}), 502
        return jsonify({"error": "DeepSeek API 回复文本为空"}), 502

    record = {"id": next(message_ids), "message": message.strip(), "reply": reply.strip()}
    messages.append(record)
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
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    record["message"] = message.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return "", 204


if __name__ == "__main__":
    app.run(port=5001, debug=False)

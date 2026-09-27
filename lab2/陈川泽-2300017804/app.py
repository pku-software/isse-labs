import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI


app = Flask(__name__, static_folder="frontend", static_url_path="/frontend")
app.json.ensure_ascii = False
load_dotenv(Path(__file__).with_name(".env"))
messages = []
next_message_id = 1
conversations = []
next_conversation_id = 1
next_turn_id = 1


def generate_reply(chat_messages):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ({"error": "服务器尚未配置 DeepSeek API Key"}, 503)

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=45.0)
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=chat_messages,
            stream=False,
            extra_body={"thinking": {"type": "disabled"}},
        )
        reply = completion.choices[0].message.content
        if not reply:
            return None, ({"error": "DeepSeek 未返回回复内容"}, 502)
        return reply, None
    except Exception:
        return None, ({"error": "DeepSeek 请求失败，请稍后重试或检查服务配置"}, 502)


def find_conversation(conversation_id):
    return next((item for item in conversations if item["id"] == conversation_id), None)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return {"message": "你好"}


@app.post("/api/messages")
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400

    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    reply, error = generate_reply([{"role": "user", "content": message}])
    if error:
        return error

    record = {"id": next_message_id, "message": message, "reply": reply}
    next_message_id += 1
    messages.append(record)
    return record, 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return {"error": "聊天记录不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400

    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    record["message"] = message
    return record


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return {"error": "聊天记录不存在"}, 404

    messages.remove(record)
    return {"message": "已删除"}


@app.post("/api/conversations")
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "请提供 JSON 格式的会话标题"}, 400
    title = data.get("title", "新会话")
    if not isinstance(title, str) or not title.strip():
        return {"error": "会话标题不能为空"}, 400

    conversation = {"id": next_conversation_id, "title": title.strip(), "messages": []}
    next_conversation_id += 1
    conversations.append(conversation)
    return conversation, 201


@app.get("/api/conversations")
def list_conversations():
    return jsonify([
        {"id": item["id"], "title": item["title"], "message_count": len(item["messages"]) // 2}
        for item in conversations
    ])


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    return conversation


@app.patch("/api/conversations/<int:conversation_id>")
def rename_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("title"), str):
        return {"error": "请提供 JSON 格式的 title 字符串"}, 400
    title = data["title"].strip()
    if not title:
        return {"error": "会话标题不能为空"}, 400

    conversation["title"] = title
    return conversation


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    conversations.remove(conversation)
    return {"message": "会话已删除"}


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_conversation_message(conversation_id):
    global next_turn_id

    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400
    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    history = [
        {"role": item["role"], "content": item["content"]}
        for item in conversation["messages"]
    ]
    reply, error = generate_reply(history + [{"role": "user", "content": message}])
    if error:
        return error

    turn_id = next_turn_id
    next_turn_id += 1
    conversation["messages"].extend([
        {"turn_id": turn_id, "role": "user", "content": message},
        {"turn_id": turn_id, "role": "assistant", "content": reply},
    ])
    return {"id": turn_id, "message": message, "reply": reply}, 201


@app.patch("/api/conversations/<int:conversation_id>/messages/<int:turn_id>")
def update_conversation_message(conversation_id, turn_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    user_message = next((item for item in conversation["messages"] if item["turn_id"] == turn_id and item["role"] == "user"), None)
    if user_message is None:
        return {"error": "聊天记录不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400
    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    user_message["content"] = message
    return {"id": turn_id, "message": message}


@app.delete("/api/conversations/<int:conversation_id>/messages/<int:turn_id>")
def delete_conversation_message(conversation_id, turn_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    if not any(item["turn_id"] == turn_id for item in conversation["messages"]):
        return {"error": "聊天记录不存在"}, 404

    conversation["messages"] = [
        item for item in conversation["messages"] if item["turn_id"] != turn_id
    ]
    return {"message": "已删除"}


if __name__ == "__main__":
    app.run(port=5001, debug=True)

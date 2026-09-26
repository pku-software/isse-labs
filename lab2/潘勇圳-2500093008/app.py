"""AI 聊天 Web 应用的后端。

当前阶段 Flask 同时提供前端页面和后端 API：

- 访问 ``GET /`` 返回 ``frontend/index.html``，样式和脚本也由 Flask 提供；
- ``GET /api/hello`` 用来确认服务是否正常运行；
- 聊天以「会话」为单位组织：一个会话里有多轮问答；
- 会话通过 ``/api/conversations`` 系列接口管理，同时保留 ``/api/messages`` 系列
  作为兼容入口（作用于默认会话）；
- 会话和消息同时保存在内存和 data/conversations.json 里，Flask 启动时会先读回这个文件，
  所以重启之后数据依然存在（不使用数据库）；
- 回复由 Flask 调用 DeepSeek API 生成，调用时会带上当前会话的历史消息作为上下文，
  API Key 只保存在本机的 .env 里。

数据结构：``{"id": 1, "title": "会话名", "messages": [{"id": 1, "message": "用户输入", "reply": "后端回复"}]}``
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
DEFAULT_CONVERSATION_TITLE = "新会话"

# 读取项目根目录下的 .env，把里面的键值对放进环境变量，
# 这样代码里只出现变量名，真实 Key 一直留在 .env 文件中
load_dotenv(BASE_DIR / ".env")

# DeepSeek 的接口地址和模型名，参考官方文档：https://api-docs.deepseek.com/zh-cn/
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 静态资源（style.css、app.js）由 Flask 从 frontend/ 目录提供，
# static_url_path="" 表示它们挂在网站根路径下，例如 /style.css
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# 让 JSON 响应里的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False

# 会话在内存里保存一份，每次改动后同步写回 conversations.json。
# 每个会话形如 {"id", "title", "messages": [{"id", "message", "reply"}]}；
# 消息 id 在所有会话之间统一递增，这样按 id 修改或删除时不会有歧义。
conversations = []
next_conversation_id = 1
next_message_id = 1


@app.get("/api/hello")
def hello():
    """最简单的接口，用于确认后端已经正常运行。"""
    return jsonify({"message": "你好"})


@app.get("/")
def index():
    """返回前端页面，这样浏览器访问 http://localhost:5001/ 就能打开它。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


def find_conversation(conversation_id):
    """按 id 查找会话，找不到时返回 None。"""
    for conversation in conversations:
        if conversation["id"] == conversation_id:
            return conversation
    return None


def find_message(message_id):
    """在所有会话里按 id 找一条消息，返回 (会话, 消息)；找不到时两者都是 None。"""
    for conversation in conversations:
        for record in conversation["messages"]:
            if record["id"] == message_id:
                return conversation, record
    return None, None


def read_json_body():
    """读取请求体里的 JSON 对象，取不到时返回空字典。"""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def read_message_text(body):
    """取出并校验 message 字段，不合法时返回 None。"""
    text = body.get("message")
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()


def read_title(body):
    """取出并校验 title 字段，不合法时返回 None。"""
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    return title.strip()


def create_conversation(title):
    """新建一个空会话并返回它。"""
    global next_conversation_id

    conversation = {"id": next_conversation_id, "title": title, "messages": []}
    conversations.append(conversation)
    next_conversation_id += 1
    return conversation


def default_conversation(create_if_missing=True):
    """给 /api/messages 兼容接口用的默认会话，也就是当前第一个会话。"""
    if conversations:
        return conversations[0]
    if create_if_missing:
        return create_conversation(DEFAULT_CONVERSATION_TITLE)
    return None


def load_data():
    """把 data/conversations.json 里的会话读回内存，供 Flask 启动时调用。"""
    global conversations, next_conversation_id, next_message_id

    if not CONVERSATIONS_FILE.exists():
        return

    try:
        with CONVERSATIONS_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        # 文件读不了或内容不是合法 JSON 时，从空数据开始，不让服务起不来
        return

    if not isinstance(data, list):
        return

    loaded = []
    for item in data:
        if not isinstance(item, dict):
            continue
        conversation_id = item.get("id")
        title = item.get("title")
        raw_messages = item.get("messages")
        if not isinstance(conversation_id, int):
            continue
        if not isinstance(title, str) or not isinstance(raw_messages, list):
            continue

        records = [
            {"id": record["id"], "message": record["message"], "reply": record["reply"]}
            for record in raw_messages
            if isinstance(record, dict)
            and isinstance(record.get("id"), int)
            and isinstance(record.get("message"), str)
            and isinstance(record.get("reply"), str)
        ]
        loaded.append({"id": conversation_id, "title": title, "messages": records})

    conversations = loaded

    # 新 id 都从已有数据的最大 id 往后接，避免和文件里的数据冲突
    next_conversation_id = max((item["id"] for item in conversations), default=0) + 1
    next_message_id = (
        max(
            (record["id"] for item in conversations for record in item["messages"]),
            default=0,
        )
        + 1
    )


def save_data():
    """把当前内存里的会话写回 data/conversations.json。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CONVERSATIONS_FILE.open("w", encoding="utf-8") as file:
        json.dump(conversations, file, ensure_ascii=False, indent=2)


# 启动时先把上次保存的会话读回内存
load_data()


def ask_deepseek(history, message):
    """把会话历史和本次提问一起发给 DeepSeek，返回模型生成的回复文本。

    history 是当前会话里已有的记录，用来给模型提供上下文。
    任何一步出错都抛出 RuntimeError，由调用方转成 JSON 错误响应，
    避免异常直接把 Flask 进程打挂。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "后端没有读到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件是否存在且内容正确"
        )

    # 历史里的每一轮问答都还原成 user / assistant 两条消息，
    # 最后再附上本次提问，模型就能基于同一会话的上下文回答
    chat_messages = []
    for record in history:
        chat_messages.append({"role": "user", "content": record["message"]})
        chat_messages.append({"role": "assistant", "content": record["reply"]})
    chat_messages.append({"role": "user", "content": message})

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": chat_messages,
        "stream": False,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"连接 DeepSeek 失败：{error}") from error

    if response.status_code != 200:
        raise RuntimeError(
            f"DeepSeek 返回错误（HTTP {response.status_code}）：{response.text[:200]}"
        )

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("DeepSeek 返回的数据格式与预期不一致") from error


@app.get("/api/conversations")
def list_conversations():
    """返回全部会话（每个会话里包含自己的消息）。"""
    return jsonify(conversations)


@app.post("/api/conversations")
def create_conversation_route():
    """新建一个会话。"""
    title = read_title(read_json_body()) or DEFAULT_CONVERSATION_TITLE
    conversation = create_conversation(title)
    save_data()
    return jsonify(conversation), 201


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    """返回指定会话及其消息。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404
    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def rename_conversation(conversation_id):
    """重命名指定会话。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    title = read_title(read_json_body())
    if title is None:
        return jsonify({"error": "请求体需要是 JSON，并且 title 字段不能为空"}), 400

    conversation["title"] = title
    save_data()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    """删除指定会话，会话里的消息也随之删除。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    conversations.remove(conversation)
    save_data()
    return jsonify({"deleted_id": conversation_id})


def create_record(conversation, text):
    """调用 DeepSeek 生成回复，把新记录加进会话并写回文件。"""
    global next_message_id

    try:
        reply = ask_deepseek(conversation["messages"], text)
    except RuntimeError as error:
        # 调用失败时不写入记录，把失败原因返回给前端显示
        return jsonify({"error": str(error)}), 502

    record = {"id": next_message_id, "message": text, "reply": reply}
    conversation["messages"].append(record)
    next_message_id += 1
    save_data()
    return jsonify(record), 201


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_conversation_message(conversation_id):
    """在指定会话里发一条消息，回复由 DeepSeek 生成。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    text = read_message_text(read_json_body())
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    return create_record(conversation, text)


@app.get("/api/messages")
def list_messages():
    """兼容入口：返回默认会话里的全部消息。"""
    conversation = default_conversation(create_if_missing=False)
    return jsonify(conversation["messages"] if conversation else [])


@app.post("/api/messages")
def create_message():
    """兼容入口：在默认会话里创建一条记录。"""
    text = read_message_text(read_json_body())
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    return create_record(default_conversation(), text)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定聊天记录的用户消息内容。"""
    conversation, record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    text = read_message_text(read_json_body())
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    record["message"] = text
    save_data()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定聊天记录。"""
    conversation, record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    conversation["messages"].remove(record)
    save_data()
    return jsonify({"deleted_id": message_id})


if __name__ == "__main__":
    # 使用 5001 端口，避免与其它本地服务冲突
    app.run(port=5001, debug=True)

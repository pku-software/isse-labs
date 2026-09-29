"""Multiple chat conversations, isolated model context, and JSON persistence."""

import json
import os
from copy import deepcopy
from itertools import count
from pathlib import Path
from threading import Lock

import requests
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

PROJECT_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False
DATA_FILE = PROJECT_DIR / "data" / "conversations.json"
LEGACY_FILE = PROJECT_DIR / "data" / "messages.json"


def read_json_list(path):
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return []
    except (OSError, UnicodeError):
        raise RuntimeError("无法读取聊天数据，请检查文件权限和编码") from None
    try:
        data = json.loads(raw) if raw.strip() else []
    except ValueError:
        raise RuntimeError("聊天数据不是有效 JSON，请修复文件后再启动") from None
    if not isinstance(data, list):
        raise RuntimeError("聊天数据最外层必须是数组")
    return data


def validate_records(records):
    if not isinstance(records, list):
        raise RuntimeError("会话中的 messages 必须是数组")
    seen = set()
    for record in records:
        if (
            not isinstance(record, dict)
            or type(record.get("id")) is not int
            or record["id"] < 1
            or record["id"] in seen
            or not isinstance(record.get("message"), str)
            or not isinstance(record.get("reply"), str)
        ):
            raise RuntimeError("聊天数据中存在无效记录或重复 ID")
        seen.add(record["id"])


def write_conversations(updated):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".json.tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(updated, file, ensure_ascii=False, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary_file, DATA_FILE)


def load_conversations():
    if DATA_FILE.exists():
        loaded = read_json_list(DATA_FILE)
    else:
        records = read_json_list(LEGACY_FILE)
        validate_records(records)
        loaded = [{"id": 1, "title": "历史记录", "messages": records}] if records else []
        # Preserve the old file. Once this file exists, it is the sole source.
        try:
            write_conversations(loaded)
        except OSError:
            raise RuntimeError("无法创建 conversations.json，请检查目录权限和磁盘空间") from None
    seen = set()
    for conversation in loaded:
        if (
            not isinstance(conversation, dict)
            or type(conversation.get("id")) is not int
            or conversation["id"] < 1
            or conversation["id"] in seen
            or not isinstance(conversation.get("title"), str)
            or not conversation["title"].strip()
        ):
            raise RuntimeError("聊天数据中存在无效会话或重复会话 ID")
        validate_records(conversation.get("messages"))
        seen.add(conversation["id"])
    return loaded


conversations = load_conversations()
conversation_ids = count(max((item["id"] for item in conversations), default=0) + 1)
message_ids = count(max((record["id"] for item in conversations for record in item["messages"]), default=0) + 1)
data_lock = Lock()


def save_conversations(updated):
    """Called under data_lock; commit memory only after the file is saved."""
    try:
        write_conversations(updated)
    except OSError:
        return jsonify(error="保存失败，请检查 data 目录权限和磁盘空间；本次修改未保存"), 500
    conversations[:] = updated
    return None


def find_conversation(id):
    return next((item for item in conversations if item["id"] == id), None)


def replace_conversation(updated):
    return save_conversations([updated if item["id"] == updated["id"] else item for item in conversations])


def read_text(field):
    if not request.is_json:
        return None, (jsonify(error="请使用 application/json 发送请求"), 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="请求体必须是有效的 JSON 对象"), 400)
    text = data.get(field)
    if not isinstance(text, str) or not text.strip():
        return None, (jsonify(error=f"{field} 必须是非空字符串"), 400)
    if field == "title" and len(text.strip()) > 100:
        return None, (jsonify(error="会话名称最多 100 个字符"), 400)
    return text.strip(), None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


def deepseek_reply(context):
    api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key or api_key == "your_api_key_here":
        return None, (jsonify(error="后端尚未配置有效的 DEEPSEEK_API_KEY，请检查容器运行时环境变量"), 503)

    # Never return upstream response bodies or exception details: they may
    # contain credentials. Only the backend sends the authorization header.
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-flash",
                "messages": context,
                "thinking": {"type": "disabled"},
                "stream": False,
                "max_tokens": 2048,
            },
            timeout=(10, 90),
            allow_redirects=False,
        )
    except requests.Timeout:
        return None, (jsonify(error="DeepSeek 请求超时，请稍后重试"), 504)
    except (requests.RequestException, UnicodeError, ValueError):
        return None, (jsonify(error="无法连接 DeepSeek，请检查后端网络和 Key 配置"), 502)

    with response:
        if response.status_code != 200:
            errors = {
                400: "DeepSeek 拒绝了请求，请检查模型调用参数",
                401: "DeepSeek 鉴权失败，请检查后端运行时 API Key 配置",
                402: "DeepSeek 账户余额不足，请检查账户余额",
                403: "DeepSeek 拒绝访问，请检查账户权限",
                429: "DeepSeek 请求过于频繁，请稍后重试",
            }
            error = errors.get(response.status_code, "DeepSeek 服务调用失败，请稍后重试")
            return None, (jsonify(error=error), 502)
        try:
            reply = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            return None, (jsonify(error="DeepSeek 返回的数据格式异常，请稍后重试"), 502)
        if not isinstance(reply, str) or not reply.strip():
            return None, (jsonify(error="DeepSeek 未返回有效文本，请稍后重试"), 502)
        return reply.strip().replace(api_key, "[已隐藏敏感信息]"), None


@app.get("/api/conversations")
def list_conversations():
    with data_lock:
        return jsonify([{"id": item["id"], "title": item["title"], "message_count": len(item["messages"])} for item in conversations])


@app.post("/api/conversations")
def create_conversation():
    title, error = read_text("title")
    if error is not None:
        return error
    with data_lock:
        conversation = {"id": next(conversation_ids), "title": title, "messages": []}
        error = save_conversations([*conversations, conversation])
        if error is not None:
            return error
        return jsonify(conversation), 201


@app.get("/api/conversations/<int:id>")
def get_conversation(id):
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        return jsonify(conversation)


@app.patch("/api/conversations/<int:id>")
def rename_conversation(id):
    title, error = read_text("title")
    if error is not None:
        return error
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        updated = {**conversation, "title": title}
        error = replace_conversation(updated)
        if error is not None:
            return error
        return jsonify(updated)


@app.delete("/api/conversations/<int:id>")
def delete_conversation(id):
    with data_lock:
        if find_conversation(id) is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        error = save_conversations([item for item in conversations if item["id"] != id])
        if error is not None:
            return error
        return jsonify(id=id, deleted=True)


@app.get("/api/conversations/<int:id>/messages")
def list_messages(id):
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        return jsonify(conversation["messages"])


@app.post("/api/conversations/<int:id>/messages")
def create_message(id):
    text, error = read_text("message")
    if error is not None:
        return error
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        history = deepcopy(conversation["messages"])
    context = []
    for record in history:
        context.append({"role": "user", "content": record["message"]})
        context.append({"role": "assistant", "content": record["reply"]})
    context.append({"role": "user", "content": text})
    reply, error = deepseek_reply(context)
    if error is not None:
        return error
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="生成回复期间会话已被删除，回复未保存"), 409
        if conversation["messages"] != history:
            return jsonify(error="生成回复期间会话记录发生变化，请刷新后重试"), 409
        record = {"id": next(message_ids), "message": text, "reply": reply}
        updated = {**conversation, "messages": [*history, record]}
        error = replace_conversation(updated)
        if error is not None:
            return error
        return jsonify(record), 201


@app.patch("/api/conversations/<int:id>/messages/<int:message_id>")
def update_message(id, message_id):
    text, error = read_text("message")
    if error is not None:
        return error
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        record = next((item for item in conversation["messages"] if item["id"] == message_id), None)
        if record is None:
            return jsonify(error="聊天记录不存在，请刷新会话"), 404
        updated_record = {**record, "message": text}
        updated = {**conversation, "messages": [updated_record if item["id"] == message_id else item for item in conversation["messages"]]}
        error = replace_conversation(updated)
        if error is not None:
            return error
        return jsonify(updated_record)


@app.delete("/api/conversations/<int:id>/messages/<int:message_id>")
def delete_message(id, message_id):
    with data_lock:
        conversation = find_conversation(id)
        if conversation is None:
            return jsonify(error="会话不存在，请刷新会话列表"), 404
        if not any(item["id"] == message_id for item in conversation["messages"]):
            return jsonify(error="聊天记录不存在，请刷新会话"), 404
        updated = {**conversation, "messages": [item for item in conversation["messages"] if item["id"] != message_id]}
        error = replace_conversation(updated)
        if error is not None:
            return error
        return jsonify(id=message_id, deleted=True)


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code


if __name__ == "__main__":
    app.run(port=5001, debug=False)

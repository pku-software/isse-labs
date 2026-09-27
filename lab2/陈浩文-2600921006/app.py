import json
import os
from itertools import count
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import APIConnectionError, APIError, APIStatusError, APITimeoutError, OpenAI

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_FILE = DATA_DIR / "conversations.json"
LEGACY_DATA_FILE = DATA_DIR / "messages.json"
MISSING_FILE = object()
data_lock = Lock()


class StorageError(Exception):
    pass


def read_json_file(path):
    try:
        contents = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return MISSING_FILE
    if not contents.strip():
        return []
    try:
        return json.loads(contents)
    except json.JSONDecodeError:
        raise ValueError(f"{path.name} 的 JSON 格式错误，请检查数据文件") from None


def validate_messages(records, seen_ids):
    if not isinstance(records, list):
        raise ValueError("messages 必须是问答记录数组")
    for record in records:
        if (
            not isinstance(record, dict)
            or type(record.get("id")) is not int
            or record["id"] < 1
            or record["id"] in seen_ids
            or not isinstance(record.get("message"), str)
            or not isinstance(record.get("reply"), str)
        ):
            raise ValueError("聊天记录数据无效，请检查数据文件")
        seen_ids.add(record["id"])


def write_conversations(records):
    temporary_file = DATA_FILE.with_suffix(".tmp")
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temporary_file.write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_file.replace(DATA_FILE)
    except (OSError, UnicodeError):
        raise StorageError from None


def load_conversations():
    records = read_json_file(DATA_FILE)
    if records is MISSING_FILE:
        # 仅在新文件不存在时迁移，保留旧文件；空数组不会触发再次导入。
        old_messages = read_json_file(LEGACY_DATA_FILE)
        if old_messages is MISSING_FILE:
            old_messages = []
        validate_messages(old_messages, set())
        records = [{"id": 1, "title": "默认会话", "messages": old_messages}]
        write_conversations(records)
        return records

    if not isinstance(records, list):
        raise ValueError("conversations.json 必须保存会话数组")
    seen_conversation_ids = set()
    seen_message_ids = set()
    for conversation in records:
        if (
            not isinstance(conversation, dict)
            or type(conversation.get("id")) is not int
            or conversation["id"] < 1
            or conversation["id"] in seen_conversation_ids
            or not isinstance(conversation.get("title"), str)
            or not conversation["title"].strip()
        ):
            raise ValueError("会话数据无效，请检查 conversations.json")
        seen_conversation_ids.add(conversation["id"])
        validate_messages(conversation.get("messages"), seen_message_ids)
    return records


conversations = load_conversations()
conversation_ids = count(max((item["id"] for item in conversations), default=0) + 1)
message_ids = count(
    max(
        (record["id"] for item in conversations for record in item["messages"]),
        default=0,
    ) + 1
)


def save_conversations(updated):
    # 调用方持有锁；文件写入成功后才更新内存。
    write_conversations(updated)
    conversations[:] = updated


def find_conversation(conversation_id):
    return next((item for item in conversations if item["id"] == conversation_id), None)


def save_updated_conversation(updated):
    save_conversations([
        updated if item["id"] == updated["id"] else item
        for item in conversations
    ])


@app.errorhandler(StorageError)
def handle_storage_error(error):
    return jsonify({"error": "会话保存失败，请检查 data 目录的写入权限和磁盘空间"}), 500


def read_text_field(field):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是有效的 JSON 对象"
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        return None, f"{field} 必须是非空字符串"
    value = value.strip()
    if field == "title" and len(value) > 80:
        return None, "会话名称不能超过 80 个字符"
    return value, None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/conversations")
def list_conversations():
    with data_lock:
        return jsonify([
            {"id": item["id"], "title": item["title"], "message_count": len(item["messages"])}
            for item in conversations
        ])


@app.post("/api/conversations")
def create_conversation():
    title, error = read_text_field("title")
    if error:
        return jsonify({"error": error}), 400
    with data_lock:
        conversation = {"id": next(conversation_ids), "title": title, "messages": []}
        save_conversations([*conversations, conversation])
        return jsonify(conversation), 201


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def rename_conversation(conversation_id):
    title, error = read_text_field("title")
    if error:
        return jsonify({"error": error}), 400
    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        updated = {**conversation, "title": title}
        save_updated_conversation(updated)
        return jsonify(updated)


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    with data_lock:
        if find_conversation(conversation_id) is None:
            return jsonify({"error": "会话不存在"}), 404
        save_conversations([item for item in conversations if item["id"] != conversation_id])
        return jsonify({"id": conversation_id, "deleted": True})


# 兼容原有接口：未指定会话的 /api/messages 路由只操作 ID 为 1 的默认会话。
@app.post("/api/messages")
@app.post("/api/conversations/<int:conversation_id>/messages")
def create_message(conversation_id=1):
    text, error = read_text_field("message")
    if error:
        return jsonify({"error": error}), 400

    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在，请创建或选择一个会话"}), 404
        history = [record.copy() for record in conversation["messages"]]

    api_messages = []
    for record in history:
        api_messages.append({"role": "user", "content": record["message"]})
        api_messages.append({"role": "assistant", "content": record["reply"]})
    api_messages.append({"role": "user", "content": text})

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        return jsonify({"error": "请在后端 .env 中设置 DEEPSEEK_API_KEY 后重启 Flask"}), 503

    try:
        with OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=60.0,
            max_retries=0,
        ) as client:
            completion = client.chat.completions.create(
                model="deepseek-flash",
                messages=api_messages,
                stream=False,
                extra_body={"thinking": {"type": "disabled"}},
            )
    except APITimeoutError:
        return jsonify({"error": "DeepSeek 响应超时，请稍后重试"}), 504
    except APIConnectionError:
        return jsonify({"error": "无法连接 DeepSeek，请检查后端网络连接"}), 502
    except APIStatusError as error:
        # 只返回本地定义的提示，不暴露供应商的原始错误或鉴权信息。
        error_messages = {
            401: "DeepSeek 认证失败，请检查后端 API Key 后重启 Flask",
            402: "DeepSeek 账户余额不足，请在开放平台检查余额",
            429: "DeepSeek 请求过于频繁，请稍后重试",
            503: "DeepSeek 服务繁忙，请稍后重试",
        }
        message = error_messages.get(error.status_code, "DeepSeek 调用失败，请稍后重试")
        status = 503 if error.status_code in {429, 503} else 502
        return jsonify({"error": message}), status
    except (APIError, ValueError):
        return jsonify({"error": "DeepSeek 调用失败，请检查后端配置后重试"}), 502

    choices = getattr(completion, "choices", None)
    reply_message = getattr(choices[0], "message", None) if isinstance(choices, list) and choices else None
    reply = getattr(reply_message, "content", None)
    if not isinstance(reply, str) or not reply.strip():
        return jsonify({"error": "DeepSeek 未返回有效的文本回复，请重试"}), 502

    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "生成回复期间会话已被删除"}), 404
        if conversation["messages"] != history:
            return jsonify({"error": "生成回复期间会话记录已改变，请重新发送"}), 409
        record = {"id": next(message_ids), "message": text, "reply": reply.strip()}
        save_updated_conversation({
            **conversation,
            "messages": [*conversation["messages"], record],
        })
        return jsonify(record), 201


@app.get("/api/messages")
@app.get("/api/conversations/<int:conversation_id>/messages")
def list_messages(conversation_id=1):
    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        return jsonify(conversation["messages"])


@app.patch("/api/messages/<int:message_id>")
@app.patch("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def update_message(message_id, conversation_id=1):
    text, error = read_text_field("message")
    if error:
        return jsonify({"error": error}), 400
    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        record = next((item for item in conversation["messages"] if item["id"] == message_id), None)
        if record is None:
            return jsonify({"error": "聊天记录不存在"}), 404
        updated_record = {**record, "message": text}
        save_updated_conversation({
            **conversation,
            "messages": [
                updated_record if item["id"] == message_id else item
                for item in conversation["messages"]
            ],
        })
        return jsonify(updated_record)


@app.delete("/api/messages/<int:message_id>")
@app.delete("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def delete_message(message_id, conversation_id=1):
    with data_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        if not any(item["id"] == message_id for item in conversation["messages"]):
            return jsonify({"error": "聊天记录不存在"}), 404
        save_updated_conversation({
            **conversation,
            "messages": [item for item in conversation["messages"] if item["id"] != message_id],
        })
        return jsonify({"id": message_id, "deleted": True})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

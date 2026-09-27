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

DATA_FILE = Path(__file__).resolve().parent / "data" / "messages.json"
messages_lock = Lock()


class StorageError(Exception):
    pass


def load_messages():
    try:
        contents = DATA_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    if not contents.strip():
        return []

    try:
        records = json.loads(contents)
    except json.JSONDecodeError:
        raise ValueError("聊天记录 JSON 格式错误，请检查 data/messages.json") from None

    if not isinstance(records, list):
        raise ValueError("data/messages.json 必须保存聊天记录数组")

    seen_ids = set()
    for record in records:
        if (
            not isinstance(record, dict)
            or type(record.get("id")) is not int
            or record["id"] < 1
            or record["id"] in seen_ids
            or not isinstance(record.get("message"), str)
            or not isinstance(record.get("reply"), str)
        ):
            raise ValueError("聊天记录数据无效，请检查 data/messages.json")
        seen_ids.add(record["id"])
    return records


messages = load_messages()
message_ids = count(max((record["id"] for record in messages), default=0) + 1)


def save_messages(updated_messages):
    # 调用方持有锁；先保存成功，再更新内存中的记录。
    temporary_file = DATA_FILE.with_suffix(".tmp")
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary_file.write_text(
            json.dumps(updated_messages, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_file.replace(DATA_FILE)
    except (OSError, UnicodeError):
        raise StorageError from None
    messages[:] = updated_messages


@app.errorhandler(StorageError)
def handle_storage_error(error):
    return jsonify({"error": "聊天记录保存失败，请检查 data 目录的写入权限和磁盘空间"}), 500


def read_message_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是有效的 JSON 对象"

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
    text, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

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
                messages=[{"role": "user", "content": text}],
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
    reply_message = getattr(choices[0], "message", None) if choices else None
    reply = getattr(reply_message, "content", None)
    if not isinstance(reply, str) or not reply.strip():
        return jsonify({"error": "DeepSeek 未返回有效的文本回复，请重试"}), 502

    with messages_lock:
        record = {"id": next(message_ids), "message": text, "reply": reply.strip()}
        save_messages([*messages, record])
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    text, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    with messages_lock:
        record = next((item for item in messages if item["id"] == message_id), None)
        if record is None:
            return jsonify({"error": "聊天记录不存在"}), 404

        updated_record = {**record, "message": text}
        save_messages([
            updated_record if item["id"] == message_id else item
            for item in messages
        ])
        return jsonify(updated_record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        record = next((item for item in messages if item["id"] == message_id), None)
        if record is None:
            return jsonify({"error": "聊天记录不存在"}), 404

        save_messages([item for item in messages if item["id"] != message_id])
        return jsonify({"id": message_id, "deleted": True})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

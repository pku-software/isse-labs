import json
import os
from pathlib import Path
from threading import Lock

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
data_file = Path(__file__).parent / "data" / "messages.json"
saved_text = data_file.read_text(encoding="utf-8") if data_file.exists() else ""
messages = json.loads(saved_text) if saved_text.strip() else []
next_id = max((item["id"] for item in messages), default=0) + 1
messages_lock = Lock()


def save_messages(updated):
    # 先写入文件，再更新内存；写入失败时保留原数据。
    data_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = data_file.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_file.replace(data_file)
    messages[:] = updated


@app.errorhandler(OSError)
def storage_error(error):
    return jsonify(error="无法保存聊天记录，请检查 data 目录权限和磁盘空间"), 500


@app.get("/")
def index():
    return app.send_static_file("index.html")


def read_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    message = data.get("message")
    return message.strip() if isinstance(message, str) else None


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    global next_id
    message = read_message()
    if not message:
        return jsonify(error="请提供非空的 message 字符串"), 400
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify(error="后端未配置 API Key，请在 .env 中配置后重启服务"), 503
    try:
        response = requests.post(
            "https://ctmoai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-5.5",
                "input": [{"role": "user", "content": message}],
                "store": False,
            },
            timeout=(10, 120),
            allow_redirects=False,
        )
        if response.status_code != 200:
            # 不返回上游响应正文，避免其中包含密钥或内部信息。
            return jsonify(error=f"模型服务请求失败（HTTP {response.status_code}），请检查密钥、额度和模型权限"), 502
        data = response.json()
        if data.get("status") != "completed":
            return jsonify(error="模型尚未完成回复，请稍后重试"), 502
        reply = "\n".join(
            part["text"]
            for item in data.get("output", [])
            if item.get("type") == "message"
            for part in item.get("content", [])
            if part.get("type") == "output_text" and isinstance(part.get("text"), str)
        ).strip()
        if not reply:
            return jsonify(error="模型服务未返回文本回复，请重试"), 502
    except requests.Timeout:
        return jsonify(error="模型服务响应超时，请稍后重试"), 504
    except requests.RequestException:
        return jsonify(error="无法连接模型服务，请检查网络后重试"), 502
    except (ValueError, TypeError, AttributeError, KeyError):
        return jsonify(error="模型服务返回的数据格式不符合 Responses API"), 502
    with messages_lock:
        record = {"id": next_id, "message": message, "reply": reply}
        save_messages(messages + [record])
        next_id += 1
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:id>")
def update_message(id):
    with messages_lock:
        record = next((item for item in messages if item["id"] == id), None)
        if record is None:
            return jsonify(error="聊天记录不存在"), 404
        message = read_message()
        if not message:
            return jsonify(error="请提供非空的 message 字符串"), 400
        record = {**record, "message": message}
        save_messages([record if item["id"] == id else item for item in messages])
    return jsonify(record)


@app.delete("/api/messages/<int:id>")
def delete_message(id):
    with messages_lock:
        record = next((item for item in messages if item["id"] == id), None)
        if record is None:
            return jsonify(error="聊天记录不存在"), 404
        save_messages([item for item in messages if item["id"] != id])
    return jsonify(message="已删除聊天记录")


if __name__ == "__main__":
    app.run(port=5001, debug=True)

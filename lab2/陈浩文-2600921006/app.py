import os
from itertools import count
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import APIConnectionError, APIError, APIStatusError, APITimeoutError, OpenAI

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

# 数据只存在于当前 Flask 进程，重启后会清空。
messages = []
message_ids = count(1)


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

    record = {"id": next(message_ids), "message": text, "reply": reply.strip()}
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

    text, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = text
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"id": message_id, "deleted": True})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

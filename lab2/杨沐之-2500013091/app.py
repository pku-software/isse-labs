import os

import httpx
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)


load_dotenv()


app = Flask(__name__, static_folder="frontend", static_url_path="")
if hasattr(app, "json"):
    app.json.ensure_ascii = False
else:
    # Flask 2.x 使用配置项控制 JSON 中的中文转义。
    app.config["JSON_AS_ASCII"] = False

messages = []
next_message_id = 1


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


def read_message_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 必须是非空字符串"

    return message.strip(), None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    message, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500

    try:
        with OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            http_client=httpx.Client(trust_env=False),
        ) as client:
            response = client.chat.completions.create(
                model="deepseek-flash",
                messages=[{"role": "user", "content": message}],
                stream=False,
            )
        reply = response.choices[0].message.content
    except AuthenticationError:
        app.logger.error("DeepSeek API 鉴权失败")
        return jsonify({"error": "DeepSeek API 鉴权失败，请检查服务器端 Key 配置"}), 502
    except RateLimitError:
        app.logger.error("DeepSeek API 请求受限")
        return jsonify({"error": "DeepSeek API 请求过于频繁，请稍后重试"}), 502
    except APIConnectionError:
        app.logger.error("无法连接 DeepSeek API")
        return jsonify({"error": "无法连接 DeepSeek API，请检查网络后重试"}), 502
    except APIStatusError as error:
        app.logger.error("DeepSeek API 返回 HTTP %s", error.status_code)
        if error.status_code == 402:
            return jsonify({"error": "DeepSeek API 账户余额不足"}), 502
        return jsonify({"error": f"DeepSeek API 返回 HTTP {error.status_code}"}), 502
    except (IndexError, AttributeError):
        app.logger.error("DeepSeek API 响应格式异常")
        return jsonify({"error": "DeepSeek API 响应格式异常"}), 502

    if not isinstance(reply, str) or not reply.strip():
        return jsonify({"error": "DeepSeek API 未返回有效回复"}), 502

    record = {
        "id": next_message_id,
        "message": message,
        "reply": reply.strip(),
    }
    messages.append(record)
    next_message_id += 1
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"message": "聊天记录已删除", "id": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

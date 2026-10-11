import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError


app = Flask(__name__, static_folder="frontend")
app.json.ensure_ascii = False
load_dotenv(override=True)
messages = []
next_message_id = 1


def message_from_request():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="请求体必须是 JSON 对象"), 400)

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, (jsonify(error="message 必须是非空字符串"), 400)

    return message.strip(), None


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:filename>")
def frontend_file(filename):
    return send_from_directory(app.static_folder, filename)


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    global next_message_id

    message, error = message_from_request()
    if error:
        return error

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify(error="未配置 DEEPSEEK_API_KEY"), 503

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message}],
        )
        reply = completion.choices[0].message.content
        if not reply:
            return jsonify(error="DeepSeek 未返回可用回复"), 502
    except AuthenticationError:
        return jsonify(error="DeepSeek API Key 无效或没有调用权限"), 502
    except RateLimitError:
        return jsonify(error="DeepSeek API 请求受限，请检查账户余额或稍后重试"), 429
    except APIConnectionError:
        return jsonify(error="无法连接 DeepSeek API，请检查网络连接"), 502
    except APIStatusError as error:
        return jsonify(error=f"DeepSeek API 返回错误状态：{error.status_code}"), 502
    except Exception:
        return jsonify(error="调用 DeepSeek API 时发生未知错误"), 502

    record = {"id": next_message_id, "message": message, "reply": reply}
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
        return jsonify(error="未找到该聊天记录"), 404

    message, error = message_from_request()
    if error:
        return error

    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify(error="未找到该聊天记录"), 404

    messages.remove(record)
    return "", 204


if __name__ == "__main__":
    app.run(port=5001, debug=True)

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
load_dotenv()
messages = []
next_message_id = 1


def error_response(message, status_code):
    return jsonify({"error": message}), status_code


def get_message_text(payload):
    if not isinstance(payload, dict):
        return None

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        return None

    return message.strip()


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


def get_ai_reply(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, error_response("DeepSeek API key is not configured", 503)

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message}],
        )
        reply = completion.choices[0].message.content
    except Exception:
        return None, error_response("DeepSeek request failed", 502)

    if not reply:
        return None, error_response("DeepSeek returned an empty reply", 502)

    return reply, None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    message = get_message_text(request.get_json(silent=True))
    if message is None:
        return error_response("message must be a non-empty string", 400)

    reply, failure_response = get_ai_reply(message)
    if failure_response is not None:
        return failure_response

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
        return error_response("message not found", 404)

    message = get_message_text(request.get_json(silent=True))
    if message is None:
        return error_response("message must be a non-empty string", 400)

    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return error_response("message not found", 404)

    messages.remove(record)
    return jsonify({"message": "deleted", "id": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

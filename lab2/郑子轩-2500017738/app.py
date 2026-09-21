from flask import Flask, jsonify


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    # TODO: Create a chat message.
    return jsonify({"error": "Not implemented"}), 501


@app.get("/api/messages")
def list_messages():
    # TODO: Return all chat messages.
    return jsonify({"error": "Not implemented"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    # TODO: Update the chat message identified by message_id.
    return jsonify({"error": "Not implemented"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    # TODO: Delete the chat message identified by message_id.
    return jsonify({"error": "Not implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)

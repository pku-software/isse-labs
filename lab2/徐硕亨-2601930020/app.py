from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "你好"})

@app.route('/api/messages', methods=['POST'])
def create_message():
    # TODO: 创建消息记录并接入 AI 回复
    return jsonify({"error": "Not Implemented"}), 501

@app.route('/api/messages', methods=['GET'])
def get_messages():
    # TODO: 获取所有消息列表
    return jsonify({"error": "Not Implemented"}), 501

@app.route('/api/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # TODO: 修改指定 ID 的消息内容
    return jsonify({"error": "Not Implemented"}), 501

@app.route('/api/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # TODO: 删除指定 ID 的消息记录
    return jsonify({"error": "Not Implemented"}), 501

if __name__ == '__main__':
    app.run(port=5001, debug=True)

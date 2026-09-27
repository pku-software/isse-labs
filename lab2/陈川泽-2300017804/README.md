# AI 聊天 Web 应用

使用 HTML、CSS、JavaScript 和 Flask 构建的多会话 AI 聊天应用。浏览器通过 Flask API 与 DeepSeek 对话，API Key 只由后端读取。

## 功能

可创建、查看、重命名、删除会话，并在不同会话中继续多轮聊天。每轮问答可修改用户消息或删除整轮。`GET /api/hello` 提供最简单的 API 示例。会话和聊天记录保存在 Flask 进程内存中。

## 数据结构

一个会话的形式为：

```json
{
  "id": 1,
  "title": "学习计划",
  "messages": [
    {"turn_id": 1, "role": "user", "content": "你好"},
    {"turn_id": 1, "role": "assistant", "content": "你好！"}
  ]
}
```

同一轮的 user 和 assistant 消息共用 `turn_id`。发送新问题时，Flask 只取当前会话中已有的 `role` / `content` 消息，再追加本次 user 消息，组成发给 DeepSeek 的 `messages` 数组。

## 安装与配置

在项目目录中执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

参照 `.env.example` 在同目录创建本地 `.env`，填入自己的 `DEEPSEEK_API_KEY`。不要提交或分享 `.env`；`.gitignore` 已将其忽略。

## 启动

在已激活的虚拟环境中运行：

```bash
python app.py
```

浏览器访问 `http://localhost:5001/`。

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/api/hello` | 返回中文问候 |
| POST / GET | `/api/conversations` | 创建会话 / 列出会话摘要 |
| GET / PATCH / DELETE | `/api/conversations/<id>` | 查看、重命名、删除会话 |
| POST | `/api/conversations/<id>/messages` | 在指定会话发送消息并获取 AI 回复 |
| PATCH / DELETE | `/api/conversations/<id>/messages/<turn_id>` | 修改用户消息 / 删除整轮问答 |
| POST / GET | `/api/messages` | 创建 / 读取独立问答记录 |
| PATCH / DELETE | `/api/messages/<id>` | 修改 / 删除独立问答记录 |

独立问答记录使用 `{ "id": 1, "message": "你好", "reply": "你好！" }` 结构。会话列表返回 `id`、`title` 和轮数 `message_count`；查看单个会话返回完整的 `messages` 数组。

最简单的 API 检查：

```bash
curl http://localhost:5001/api/hello
curl -X POST http://localhost:5001/api/conversations \
  -H 'Content-Type: application/json' \
  -d '{"title":"测试会话"}'
curl -X POST http://localhost:5001/api/conversations/1/messages \
  -H 'Content-Type: application/json' \
  -d '{"message":"你好"}'
```

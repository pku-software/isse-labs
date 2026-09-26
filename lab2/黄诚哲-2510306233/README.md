# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：

- 前端使用 HTML + CSS + JavaScript；
- 后端使用 Python + Flask；
- 前端通过 `fetch()` 调用自己的 Flask API；
- Flask 后端调用 DeepSeek API 获得真实 AI 回复。

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 配置环境变量

从示例文件复制一份本地 `.env`：

```bash
cp .env.example .env
```

然后编辑 `.env`，把 `DEEPSEEK_API_KEY` 的值替换为你的真实 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已被 `.gitignore` 忽略，不会提交到 Git；`.env.example` 只包含示例值。

## 启动与访问

```bash
python app.py
```

浏览器访问 `http://localhost:5001/` 即可打开聊天页面。

## 数据持久化与多会话

聊天数据保存在 `data/conversations.json`。文件最外层是一个会话数组，每个会话包含多条消息：

```json
[
  {
    "id": 1,
    "title": "会话标题",
    "messages": [
      { "id": 1, "role": "user", "content": "用户输入" },
      { "id": 2, "role": "assistant", "content": "后端回复" }
    ]
  }
]
```

每次创建、修改或删除会话或消息后，后端都会把内存中的完整数据写回该文件；启动时再从这个文件读入内存，因此 Flask 重启后数据仍然保留。

## API 设计

- `POST /api/conversations` 创建会话
- `GET /api/conversations` 列出全部会话
- `GET /api/conversations/<id>` 获取单个会话
- `PATCH /api/conversations/<id>` 重命名会话
- `DELETE /api/conversations/<id>` 删除会话
- `POST /api/conversations/<id>/messages` 在会话中发送消息
- `PATCH /api/conversations/<id>/messages/<mid>` 修改消息
- `DELETE /api/conversations/<id>/messages/<mid>` 删除消息

发送消息时，后端会把该会话已有的全部历史消息（`role` + `content`）连同本次新问题一起作为 `messages` 数组发送给 DeepSeek，从而让模型获得上下文、实现多轮对话；不同会话的历史彼此隔离。

## 快速 API 测试

健康检查：

```bash
curl http://localhost:5001/api/hello
```

创建会话：

```bash
curl -X POST http://localhost:5001/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"我的会话"}'
```

列出会话：

```bash
curl http://localhost:5001/api/conversations
```

在会话中发送消息（`<id>` 替换为真实会话 ID）：

```bash
curl -X POST http://localhost:5001/api/conversations/<id>/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}'
```

## 选做功能

- JSON 文件持久化：会话与消息保存在 `data/conversations.json`，Flask 重启后仍保留；
- 多会话与多轮对话：支持创建、重命名、删除会话，每个会话维护独立的上下文并传给 DeepSeek。

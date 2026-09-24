# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：

- 前端使用 HTML + CSS + JavaScript；
- 后端使用 Python + Flask；
- 前端通过 `fetch()` 调用自己的 Flask API；
- Flask 后端调用 DeepSeek API 获得真实 AI 回复。

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

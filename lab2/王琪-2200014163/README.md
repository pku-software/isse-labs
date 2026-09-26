# AI 聊天 Web 应用

一个基于 Flask + DeepSeek 的多会话 AI 聊天应用。前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask，通过 DeepSeek API 生成回复。

## 功能

- 支持创建、重命名、删除多个聊天会话；
- 每个会话内进行多轮对话，模型能记住会话历史；
- 支持修改、删除单条用户消息；
- 修改用户消息后会重新生成回复。

## 数据模型

- 会话（conversation）：`{"id": 1, "title": "标题", "messages": [...]}`
- 消息（message）：`{"id": 1, "role": "user" | "assistant", "content": "文本"}`

## API 设计

- `POST /api/conversations`：创建会话
- `GET /api/conversations`：列出会话
- `GET /api/conversations/<id>`：获取单个会话
- `PATCH /api/conversations/<id>`：重命名会话
- `DELETE /api/conversations/<id>`：删除会话
- `POST /api/conversations/<id>/messages`：发送消息（调用 DeepSeek）
- `PATCH /api/conversations/<id>/messages/<mid>`：修改消息
- `DELETE /api/conversations/<id>/messages/<mid>`：删除消息

## DeepSeek 上下文

发送消息时，后端会把当前会话的完整历史（所有 user/assistant 消息）作为 `messages` 数组发给 DeepSeek，使模型能够基于前文进行多轮对话。

# AI 聊天 Web 应用

## 项目简介

一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。前端通过 Flask API 管理聊天记录，后端负责安全调用 AI 服务。

## 功能

- 创建、查看、切换、重命名和删除多个聊天会话；
- 在每个会话中进行多轮 AI 对话；
- 不同会话的历史消息彼此隔离；
- 使用 JSON 文件持久化会话，Flask 重启后仍可恢复；
- DeepSeek API Key 仅由 Flask 后端读取。

## 配置与启动

待项目实现后补充。

## API

### 数据结构

每个 conversation 包含 `id`、`title` 和 `messages`。每条 message 包含唯一 `id`、表示发言者的 `role`，以及消息正文 `content`。

```json
{
  "id": 1,
  "title": "示例会话",
  "messages": [
    {"id": 1, "role": "user", "content": "你好"},
    {"id": 2, "role": "assistant", "content": "你好！"}
  ]
}
```

完整 conversation 列表保存在 `data/conversations.json`，文件最外层是 JSON 数组。创建、重命名、删除会话或新增消息时，Flask 会先更新内存中的 `conversations`，再立即把完整列表写回该文件。Flask 启动时读取文件并恢复内存数据，同时根据已有最大 ID 生成后续 ID。

### 会话接口

- `POST /api/conversations`：创建会话；
- `GET /api/conversations`：获取会话列表；
- `GET /api/conversations/<id>`：获取一个会话及其消息；
- `PATCH /api/conversations/<id>`：重命名会话；
- `DELETE /api/conversations/<id>`：删除会话；
- `POST /api/conversations/<id>/messages`：在指定会话中发送消息。

发送新问题时，Flask 会按原顺序把当前 conversation 已有的 `user` 与 `assistant` 消息转换为 DeepSeek 所需的 `messages` 数组，再把本次 `user` 消息追加到末尾。会话标题、消息数量和其他会话的内容不会发送给模型。

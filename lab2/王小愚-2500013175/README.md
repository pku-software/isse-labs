# AI 聊天 Web 应用

一个使用 HTML、CSS、JavaScript 和 Flask 构建的简易 AI 聊天应用。前端通过 Flask API 管理聊天记录，后端负责安全调用 AI 服务。

## 功能

- 创建、查看、重命名和删除多个聊天会话；
- 在每个会话中进行多轮 AI 对话；
- 修改或删除已有问答；
- 将会话和消息持久化保存到 JSON 文件；
- API Key 仅由 Flask 后端从环境变量读取。

## 安装与配置

待项目实现后补充。

## 启动方式

待项目实现后补充。

## API

### 多会话数据结构

每个 conversation 包含唯一 ID、标题和消息数组：

```json
{
  "id": 1,
  "title": "新对话",
  "messages": [
    {"id": 1, "role": "user", "content": "用户问题"},
    {"id": 2, "role": "assistant", "content": "AI 回复"}
  ]
}
```

`role` 区分用户消息和 AI 回复。当用户发送新问题时，后端会把当前 conversation 中已有的 `messages` 和新问题一起发给 DeepSeek，不会加入其他 conversation 的消息。

### JSON 持久化

所有 conversation 以数组形式保存在 `data/conversations.json`。Flask 启动时读取该文件；创建、重命名或删除会话，以及新增、修改或删除消息后，后端会立即将最新数据写回文件。新会话和新消息的 ID 会从已有最大 ID 之后继续生成。

### 会话 API

- `POST /api/conversations`：创建会话；
- `GET /api/conversations`：获取会话列表；
- `GET /api/conversations/<id>`：获取指定会话及其消息；
- `PATCH /api/conversations/<id>`：重命名会话；
- `DELETE /api/conversations/<id>`：删除会话；
- `POST /api/conversations/<id>/messages`：在指定会话中发送新消息；
- `PATCH /api/conversations/<id>/messages/<message_id>`：修改用户消息；
- `DELETE /api/conversations/<id>/messages/<message_id>`：删除一轮问答。

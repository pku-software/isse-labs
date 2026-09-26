# AI 聊天 Web 应用

使用 HTML、CSS 和 JavaScript 构建浏览器界面，使用 Python 和 Flask 提供后端 API。

## 项目功能

## 安装依赖

## 环境配置

## 启动与访问

## API 用法

请求与响应均使用 JSON（删除成功返回空响应），请求体需带 `Content-Type: application/json`。

### 会话接口

- `POST /api/conversations`：以 `{"title":"旅行计划"}` 创建会话，返回完整会话和 `201`。
- `GET /api/conversations`：返回会话摘要数组，每项包含 `id`、`title`、`message_count`（问答轮数）。
- `GET /api/conversations/<id>`：返回该会话及全部问答记录。
- `PATCH /api/conversations/<id>`：以 `{"title":"新名称"}` 重命名，返回更新后的完整会话。
- `DELETE /api/conversations/<id>`：删除会话及其问答，成功返回 `204`。
- `POST /api/conversations/<id>/messages`：以 `{"message":"我的问题"}` 提问，返回新问答记录 `{id, message, reply}` 和 `201`。
- `GET /api/conversations/<id>/messages`：返回该会话的问答数组。
- `PATCH /api/conversations/<id>/messages/<message_id>`：以 `{"message":"修改后的问题"}` 修改问题，返回更新后的记录，已有回答不重新生成。
- `DELETE /api/conversations/<id>/messages/<message_id>`：删除一轮问答，成功返回 `204`。

会话名称去除首尾空白后须为 1–100 个字符，问题须为 1–4000 个字符。消息 ID 在全部现有会话中唯一。不存在的会话或消息返回 `404`；无效 JSON、字段或长度返回 `400`，不支持的请求内容类型返回 `415`。错误响应格式为 `{"error":"错误说明"}`。

### 兼容接口

- `GET /api/hello`：返回 `{"message":"你好"}`。
- `GET /api/messages`：返回所有会话的问答记录。
- `POST /api/messages`：请求体仍为 `{"message":"我的问题"}`，向列表中的第一个会话提问；无会话时先创建“默认会话”。
- `PATCH /api/messages/<id>`、`DELETE /api/messages/<id>`：按全局消息 ID 修改或删除一轮问答。

网页使用带会话 ID 的接口，使每次操作明确属于当前会话。

## API 测试

## 可选功能

### JSON 持久化

会话及聊天记录保存在项目目录下的 `data/conversations.json` 中，文件路径相对于 `app.py` 确定，不受启动终端所在目录影响。最外层是会话数组，每个会话包含 `id`、`title` 和 `messages`；`messages` 中每个对象是一轮用户问题与 AI 回答：

```json
[
  {
    "id": 1,
    "title": "旅行计划",
    "messages": [
      {"id": 1, "message": "我想去杭州", "reply": "你计划游玩几天？"}
    ]
  }
]
```

- Flask 启动时加载文件，空文件或空数组表示没有会话。文件格式损坏时停止启动并提示修复，避免覆盖原数据。
- 只有 `conversations.json` 不存在时，才将旧版 `data/messages.json` 中的记录迁入“历史记录”会话，并生成新文件；没有旧记录则生成空数组。旧文件保留为迁移备份，正常运行不再读写它。请勿将删除新文件当作清空数据的方式，否则下次启动会重新迁移旧备份。
- 创建、重命名、删除会话或增删改问答后，将完整的会话集合写入临时文件，再替换正式文件；保存成功后更新内存。读取不会修改文件。
- 保存失败时返回 JSON 错误，已有内存记录保持不变。修改问题不会重新生成该条记录的 AI 回复。
- 重启后分别根据现有会话和消息的最大 ID 分配后续 ID，避免与现有记录冲突。

可创建记录后检查文件，再停止并重新启动 Flask、刷新页面，验证记录仍然存在。本地文件存储适用于单个 Flask 进程，不支持多个服务进程同时写入同一文件。

### 多会话与多轮上下文

页面支持创建、选择、重命名和删除会话，各会话分别保存问答。首次加载页面时选择列表中的第一个会话；切换会话时，尚未发送的问题暂存在当前页面内存中，刷新页面后草稿会丢失。

后端调用 DeepSeek 时，将当前会话最近 10 轮问答按时间正序转换为交替的 `user`、`assistant` 消息，再追加本次 `user` 问题。不发送 `system` 消息、其他会话的记录或会话名称。完整历史仍保存在本地，10 轮限制只作用于发送给模型的上下文。

请求使用 `model: deepseek-flash`、`thinking: {"type":"disabled"}`、`stream: false` 和 `max_tokens: 2048`。API Key 只由后端读取并放入请求头，不返回给浏览器。模型不会通过本地会话 ID 自动取得历史，上下文由应用在每次请求中提供。

修改问题不会重新生成已有回答；后续请求使用修改后的历史。删除问答后，该轮不再直接进入上下文，但其他保留回答可能仍引用它。等待模型回复期间，若同一会话的记录被其他请求更改，返回 `409` 并提示刷新重试，避免保存基于旧历史的回答；若会话已被删除则返回 `404`。

# AI 聊天 Web 应用

基于 HTML、CSS、JavaScript 与 Python Flask 的 AI 聊天 Web 项目。

## 项目功能

## 安装依赖

## 环境配置

## 启动与访问

## API 用法

## 会话和数据持久化

会话与问答保存在项目根目录的 `data/conversations.json`，最外层是数组：

```json
[
  {
    "id": 1,
    "title": "旅行计划",
    "messages": [
      {"id": 1, "message": "推荐一个旅行目的地", "reply": "可以考虑杭州。"}
    ]
  }
]
```

`conversation.id` 标识会话，`title` 是名称，`messages` 按时间顺序保存问答。每条问答包含 `id`、用户问题 `message` 和模型回答 `reply`。修改问题不会重新生成已有回答；后续提问将使用修改后的历史。删除问答会将该问题和回答一起移除。

每次调用 DeepSeek 时，后端把当前会话的历史问答依次转换为 `role: user` 和 `role: assistant` 消息，再将本次新问题作为最后一条 `user` 消息，传入请求的 `messages` 数组。其他会话不会被加入上下文。

启动时读取 `data/conversations.json`。首次升级且该文件不存在时，将旧 `data/messages.json` 的记录迁入“历史记录”会话，并保留旧文件。之后只读写 `conversations.json`，旧文件作为迁移前备份；空文件或无旧数据时从空数组开始。

会话或问答创建、修改、删除后，先写临时文件再替换正式文件，保存成功后才更新内存。写入失败返回 JSON 错误。无效 JSON、无效结构或重复 ID 会阻止启动，避免覆盖已有数据。新 ID 从已加载数据的最大 ID 加一开始。此实现适用于单个 Flask 服务进程。

## 会话 API

请求及响应使用 JSON。请求体使用 `Content-Type: application/json`。以下 `id` 为会话 ID，`message_id` 为该会话内问答 ID。

| 方法 | 路径 | 请求体或作用 |
| --- | --- | --- |
| GET | `/api/hello` | 返回问候信息 |
| GET | `/api/conversations` | 返回会话摘要数组，含 `id`、`title`、`message_count`（问答数） |
| POST | `/api/conversations` | `{"title":"旅行计划"}`，创建会话 |
| GET | `/api/conversations/<id>` | 返回会话及全部问答 |
| PATCH | `/api/conversations/<id>` | `{"title":"新的名称"}`，重命名 |
| DELETE | `/api/conversations/<id>` | 删除会话及其问答 |
| GET | `/api/conversations/<id>/messages` | 返回当前会话问答数组 |
| POST | `/api/conversations/<id>/messages` | `{"message":"你的问题"}`，携带当前会话上下文调用模型 |
| PATCH | `/api/conversations/<id>/messages/<message_id>` | `{"message":"修改后的问题"}`，仅修改问题 |
| DELETE | `/api/conversations/<id>/messages/<message_id>` | 删除一条问答 |

创建成功返回 `201`，其余成功请求返回 `200`。错误返回 `{"error":"说明"}`：无效输入 `400`，不存在 `404`，并发修改冲突 `409`，非 JSON 请求体 `415`，写入失败 `500`，模型调用失败 `502`，Key 未配置 `503`，模型超时 `504`。

多会话版本用上述会话内消息接口替代旧 `/api/messages` 接口。一次问答仍以 `{id, message, reply}` 返回。生成回复期间若同一会话记录被修改或删除，返回冲突提示，请刷新后重试。

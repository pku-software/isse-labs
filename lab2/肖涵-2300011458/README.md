# AI 聊天 Web 应用

## 项目说明

本项目使用 HTML、CSS、JavaScript 和 Python Flask 构建一个支持多个会话的 AI 聊天 Web 应用。前端只调用 Flask API，Flask 在后端安全读取 DeepSeek API Key 并调用模型。

## 会话与消息结构

每个 conversation 包含：

- `id`：会话的唯一标识；
- `title`：会话名称；
- `messages`：按时间顺序保存的消息数组。

每条 message 包含：

- `id`：消息的唯一标识；
- `turn_id`：同一轮用户问题和模型回答共享的标识；
- `role`：`user` 或 `assistant`；
- `content`：消息正文。

当前 conversation 和 message 保存在 Flask 进程内存中，重启 Flask 后会清空。

## 安装与启动

待项目实现后补充依赖安装、环境配置和启动方法。

## API 用法

- `POST /api/conversations`：创建会话；
- `GET /api/conversations`：获取会话列表；
- `GET /api/conversations/<id>`：获取一个会话及其消息；
- `PATCH /api/conversations/<id>`：重命名会话；
- `DELETE /api/conversations/<id>`：删除会话；
- `POST /api/conversations/<id>/messages`：在会话中发送新消息；
- `PATCH /api/conversations/<id>/messages/<message_id>`：修改用户消息；
- `DELETE /api/conversations/<id>/messages/<message_id>`：删除一轮问答。

发送新问题时，Flask 会把当前 conversation 中已有的 `user` 和 `assistant` 消息按顺序组成 DeepSeek `messages` 数组，再追加本次新的 `user` 消息。这样模型可以获得当前会话所需的历史上下文，同时不会混入其他会话的内容。模型回复后，Flask 将本次用户消息和 `assistant` 回复写回当前 conversation。

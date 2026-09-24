# AI 聊天 Web 应用

一个使用 HTML、CSS、JavaScript 和 Flask 构建的简易 AI 聊天应用。前端通过 Flask API 管理聊天记录，后端负责安全调用 AI 服务。

## 功能

- 创建、查看、重命名和删除多个聊天会话；
- 在每个会话中进行多轮 AI 对话；
- 修改或删除已有问答；
- 将会话和消息持久化保存到 JSON 文件；
- API Key 仅由 Flask 后端从环境变量读取。

## 安装与配置

1. 进入项目目录，安装 Python 依赖：

   ```bash
   python -m pip install -r requirements.txt
   ```

2. 根据模板创建本地配置：

   ```bash
   cp .env.example .env
   ```

3. 在 `.env` 中配置自己的 DeepSeek API Key：

   ```dotenv
   DEEPSEEK_API_KEY=你的真实APIKey
   ```

`.env` 已由 `.gitignore` 忽略，不应提交到 Git。`.env.example` 只包含可公开的占位值。

## 启动方式

运行：

```bash
python app.py
```

服务默认监听 `5001` 端口。启动后在浏览器访问：

```text
http://localhost:5001/
```

页面可以创建多个会话、切换会话、进行多轮对话，以及重命名或删除会话。

## API

### 基础 API

- `GET /api/hello`：返回中文问候；
- `POST /api/messages`：创建一条独立问答记录；
- `GET /api/messages`：获取当前进程内的独立问答记录；
- `PATCH /api/messages/<id>`：修改独立记录的用户消息；
- `DELETE /api/messages/<id>`：删除独立问答记录。

多会话页面使用下方的会话 API；基础 `/api/messages` 接口保留用于独立问答和 API 测试，其数据只保存在当前 Python 进程中。

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

### API 测试

服务启动后，可用以下命令测试基础响应：

```bash
curl http://localhost:5001/api/hello
```

查看所有会话：

```bash
curl http://localhost:5001/api/conversations
```

创建一个会话：

```bash
curl -X POST http://localhost:5001/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"测试会话"}'
```

向会话发送消息时，将 `<conversation_id>` 替换为已创建会话的 ID：

```bash
curl -X POST http://localhost:5001/api/conversations/<conversation_id>/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

## 选做功能

- 已完成 JSON 文件持久化；
- 已完成多会话和多轮对话。

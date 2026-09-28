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

### 1. 安装依赖

进入项目目录后运行：

```bash
python -m pip install -r requirements.txt
```

### 2. 配置 DeepSeek API Key

复制 `.env.example` 为 `.env`，并把示例值替换为自己的 DeepSeek API Key：

```dotenv
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已加入 `.gitignore`，不要将其提交到 Git，也不要把真实 Key 写入前端代码。

### 3. 启动 Flask

```bash
python app.py
```

服务默认监听 `5001` 端口。启动后在浏览器访问：

```text
http://localhost:5001/
```

聊天记录保存在 `data/conversations.json`。创建、修改或删除会话和消息后文件会自动更新。

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

- `GET /api/hello`：返回基础问候，用于检查 Flask 是否正常运行；
- `POST /api/conversations`：创建会话；
- `GET /api/conversations`：获取会话列表；
- `GET /api/conversations/<id>`：获取一个会话及其消息；
- `PATCH /api/conversations/<id>`：重命名会话；
- `DELETE /api/conversations/<id>`：删除会话；
- `POST /api/conversations/<id>/messages`：在指定会话中发送消息。

发送新问题时，Flask 会按原顺序把当前 conversation 已有的 `user` 与 `assistant` 消息转换为 DeepSeek 所需的 `messages` 数组，再把本次 `user` 消息追加到末尾。会话标题、消息数量和其他会话的内容不会发送给模型。

## API 测试

启动 Flask 后，可先检查基础接口：

```bash
curl http://localhost:5001/api/hello
```

创建会话：

```bash
curl -X POST http://localhost:5001/api/conversations -H "Content-Type: application/json" -d '{"title":"测试会话"}'
```

假设返回的会话 ID 为 `1`，可发送消息：

```bash
curl -X POST http://localhost:5001/api/conversations/1/messages -H "Content-Type: application/json" -d '{"message":"请用一句话介绍北京大学"}'
```

在 Windows PowerShell 中使用 `curl.exe` 时，如果 JSON 引号被错误解析，可将请求数据中的双引号写成 `\"`。

## 已实现的选做功能

- JSON 文件持久化：使用 `data/conversations.json` 保存并恢复全部会话；
- 多会话与多轮对话：支持会话管理、上下文隔离和携带当前会话历史调用 DeepSeek。

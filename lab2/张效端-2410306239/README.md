# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：Flask 后端 + 原生前端，接入 DeepSeek API 实现真实 AI 回复，支持多会话与多轮对话，聊天数据持久化到 JSON 文件。

## 项目结构

- `app.py`：Flask 后端
- `frontend/`：前端页面（HTML + CSS + JavaScript）
- `data/conversations.json`：会话与聊天记录持久化文件
- `.env.example`：环境变量模板（真实 `.env` 不会被提交）

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括 `flask`、`python-dotenv`、`openai`。

## 配置 API Key

1. 复制模板创建本地配置文件：

   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env`，把示例值替换为你在 [DeepSeek 开放平台](https://platform.deepseek.com/) 创建的 API Key：

   ```
   DEEPSEEK_API_KEY=你的真实Key
   ```

`.env` 已被 `.gitignore` 忽略，不会被提交到 Git。

## 启动

```bash
python app.py
```

Flask 监听 5001 端口。启动后用浏览器访问：

```
http://localhost:5001/
```

## API

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/api/conversations` | 创建会话 |
| GET | `/api/conversations` | 查看全部会话 |
| GET | `/api/conversations/<id>` | 查看指定会话（含消息） |
| PATCH | `/api/conversations/<id>` | 重命名会话 |
| DELETE | `/api/conversations/<id>` | 删除会话 |
| POST | `/api/conversations/<id>/messages` | 在会话中发送消息 |
| GET | `/api/hello` | 连通性测试 |

### 最简单的 API 测试

保持 Flask 运行，另开一个终端：

```bash
# 连通性测试
curl http://localhost:5001/api/hello

# 创建会话
curl -X POST http://localhost:5001/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"测试会话"}'

# 在会话中发送消息（会话 id 以上一步返回为准）
curl -X POST http://localhost:5001/api/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}'

# 查看全部会话
curl http://localhost:5001/api/conversations
```

## 数据结构与持久化

会话保存在 `data/conversations.json`，文件内容为一个 JSON 数组，每个会话的结构：

```json
{
  "id": 1,
  "title": "会话标题",
  "messages": [
    {"id": 1, "message": "用户输入", "reply": "AI 回复"}
  ]
}
```

- Flask 启动时读取该文件；文件不存在或内容异常时从空数据开始
- 每次创建、修改、删除会话或发送消息后立即写回文件
- 会话 id 与消息 id 都从已有最大 id + 1 续接，不与已有记录冲突

## 多轮对话上下文

在某个会话中发送新消息时，后端把该会话的历史消息按 `user`/`assistant` 角色依次拼入请求的 `messages` 数组，最后附上本次新问题，一起发给 DeepSeek；模型返回的文本作为 `reply` 存入该会话。DeepSeek API 本身无状态，"记忆"由后端在每次请求时重建上下文来实现。

## 已完成的选做功能

- JSON 文件持久化：聊天数据保存在 `data/conversations.json`，Flask 重启后数据不丢失
- 多会话多轮对话：支持创建、切换、重命名、删除会话，每个会话拥有独立的历史上下文

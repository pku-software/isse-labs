# AI 聊天 Web 应用（支持多会话与上下文）

本项目是一个基于 Flask 和原生 JavaScript 搭建的轻量级 AI 聊天 Web 应用，支持前后端分离通信、会话管理、多轮对话上下文记忆、消息 CRUD（增删改查）以及接入 DeepSeek 官方大模型进行智能对话。

## 功能介绍
- **原生前端界面**：采用 HTML5 + CSS3 + 原生 JavaScript 构建，提供侧边栏会话列表与对话视窗。
- **Flask RESTful API**：后端使用 Python + Flask 提供标准 RESTful 接口。
- **多会话管理**：支持创建、切换、重命名和删除独立会话。
- **多轮对话上下文**：向模型提问时自动携带当前会话历史消息，实现连贯的上下文理解。
- **安全金钥管理**：通过本地 `.env` 管理 API Key，配合 `.gitignore` 杜绝金钥外泄。

## 数据结构设计

### 1. Conversation（会话）
```json
{
  "id": 1,
  "title": "会话名称",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "你好，我叫徐硕亨"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "你好！徐硕亨同学，请问有什么可以帮助你？"
    }
  ]
}
```

### 2. Message（单条消息）
- `id`：整数，消息唯一标识符。
- `role`：字符串，取值为 `"user"`（用户）或 `"assistant"`（AI 回复）。
- `content`：字符串，消息具体文本内容。

### 3. 传给 DeepSeek API 的上下文组成
因为大语言模型本身是无状态（Stateless）的，为了让模型具备上下文记忆，我们在每次调用时将当前会话的历史消息数组（只包含 `role` 和 `content`）与用户最新提问拼接成完整的 `messages` 列表发送：
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "你好，我叫徐硕亨"},
    {"role": "assistant", "content": "你好！徐硕亨同学"},
    {"role": "user", "content": "我刚才说我叫什么名字？"}
  ],
  "stream": false
}
```

### 4. 数据持久化设计（JSON 文件持久化）
- **持久化文件位置**：`data/conversations.json`
- **数据结构**：最外层为会话对象构成的列表数组（Array），每个会话包含 `id`、`title` 以及 `messages` 列表。
- **机制原理**：
  - Flask 启动时自动从 `data/conversations.json` 载入历史数据至内存；
  - 任何创建、修改、删除会话或消息的操作，都会即时序列化并写回该文件；
  - 保证服务重启或系统关机后数据不丢失。


## 环境依赖与安装
```bash
pip install -r requirements.txt
```

## 环境变量配置
1. 复制配置文件范本：
   ```bash
   cp .env.example .env
   ```
2. 在 `.env` 中填写您的 DeepSeek API Key：
   ```text
   DEEPSEEK_API_KEY=你的真实APIKey
   ```

## 启动方式
```bash
python app.py
```
启动后在浏览器中访问：
`http://localhost:5001/`

## API 规格说明

| 请求方法 | 路由路径 | 描述 |
| :--- | :--- | :--- |
| `GET` | `/api/hello` | 基础连线健康检查 |
| `GET` | `/api/conversations` | 获取所有会话列表（摘要） |
| `POST` | `/api/conversations` | 创建新会话 |
| `GET` | `/api/conversations/<id>` | 获取指定会话详情与完整消息 |
| `PATCH` | `/api/conversations/<id>` | 重命名指定会话标题 |
| `DELETE` | `/api/conversations/<id>` | 删除指定会话 |
| `POST` | `/api/conversations/<id>/messages` | 在指定会话中发送新提问并获取 AI 回复 |
| `PATCH` | `/api/conversations/<cid>/messages/<mid>` | 修改指定会话内的单条消息内容 |
| `DELETE` | `/api/conversations/<cid>/messages/<mid>` | 删除指定会话内的单条消息 |

## API 简单测试范例
```bash
# 1. 连线测试
curl http://localhost:5001/api/hello

# 2. 获取会话列表
curl http://localhost:5001/api/conversations

# 3. 在会话 1 中发送消息
curl -X POST http://localhost:5001/api/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

## 完成的选做功能说明
1. **选做任务 1：使用 JSON 文件持久化**
   - 实现了将会话与全部历史消息即时序列化并持久化存储在 `data/conversations.json` 中。
   - 服务重启或计算机关机后，重新启动 Flask 应用能够完整读取并恢复所有历史会话与对话内容。
2. **选做任务 2：支持多个聊天会话与多轮对话上下文**
   - 前端提供侧边栏会话列表，具备新建会话、切换会话、重命名会话、删除会话等完整功能。
   - 每次调用 DeepSeek API 时，自动将当前会话的历史消息数组打包为上下文一同传给模型，实现连贯的多轮对话能力。


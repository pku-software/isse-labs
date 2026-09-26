# AI 聊天 Web 应用

## 项目简介

这是一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。前端通过 `fetch()` 请求 Flask API，后端使用本地环境变量中的 API Key 调用 DeepSeek，并以 JSON 格式向前端返回结果。

项目支持：

- 在浏览器中与 DeepSeek 进行问答；
- 创建、查看、修改和删除聊天记录；
- 创建、切换、重命名和删除多个聊天会话；
- 在同一会话中将历史消息作为 DeepSeek 的上下文；
- 使用 JSON 文件持久化保存会话与消息；
- 在页面内显示操作状态、错误和删除确认；
- 将 DeepSeek API Key 仅保存在后端的 `.env` 中。

## 项目结构

```text
.
├── app.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/
│   └── conversations.json
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 安装依赖

建议使用 Python 3.10 或更高版本。进入项目目录后执行：

```bash
python -m pip install -r requirements.txt
```

## 配置 API Key

复制示例配置：

```bash
cp .env.example .env
```

编辑新建的 `.env`，将占位值替换为自己的 DeepSeek API Key：

```dotenv
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 已在 `.gitignore` 中排除，不应提交到 Git。`.env.example` 只保留示例值。

## 启动应用

```bash
python app.py
```

Flask 默认在 `5001` 端口启动。在浏览器访问：

```text
http://localhost:5001/
```

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/hello` | 返回服务问候信息 |
| `POST` | `/api/messages` | 向 DeepSeek 发送消息并创建聊天记录 |
| `GET` | `/api/messages` | 返回全部聊天记录 |
| `PATCH` | `/api/messages/<id>` | 修改指定记录的用户消息 |
| `DELETE` | `/api/messages/<id>` | 删除指定聊天记录 |
| `POST` | `/api/conversations` | 创建会话 |
| `GET` | `/api/conversations` | 返回全部会话 |
| `GET` | `/api/conversations/<id>` | 返回指定会话及其消息 |
| `PATCH` | `/api/conversations/<id>` | 重命名指定会话 |
| `DELETE` | `/api/conversations/<id>` | 删除指定会话及其消息 |
| `POST` | `/api/conversations/<id>/messages` | 在指定会话中发送新消息 |

会话的 JSON 格式为：

```json
{
  "id": 1,
  "title": "校园生活",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "北京大学在哪里？"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "DeepSeek 的回复"
    }
  ]
}
```

`/api/messages` 路由保留原有单列表 CRUD 接口的兼容能力；多会话页面使用 `/api/conversations` 路由。

## 简单 API 测试

测试 Flask 是否正常运行：

```bash
curl http://localhost:5001/api/hello
```

创建一条聊天记录：

```bash
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

创建一个会话：

```bash
curl -X POST http://localhost:5001/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"校园生活"}'
```

假设新会话的 ID 为 `1`，在该会话中发送消息：

```bash
curl -X POST http://localhost:5001/api/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"北京大学在哪里？"}'
```

## 数据存储

会话与消息持久化保存在 `data/conversations.json` 中。文件最外层是 JSON 数组，每个元素是一个 conversation；每个 conversation 包含 `id`、`title` 和按时间顺序排列的 `messages` 数组。

Flask 启动时读取该文件，创建、重命名或删除会话以及创建、修改或删除消息后，都会立即将完整数组写回文件。

## DeepSeek 上下文

用户在某个会话中发送新问题时，Flask 只读取当前 conversation 的 `messages` 数组，按原有顺序保留每条消息的 `role` 和 `content`，再追加本次的 `user` 消息后发给 DeepSeek。`user` 表示用户消息，`assistant` 表示模型回复。其他会话的历史不会加入该请求。

## 错误响应

所有 API 错误都以 JSON 返回，前端会在页面内显示提示：

- `400` 表示请求体缺失或内容无效；
- `404` 表示会话或聊天记录不存在；
- `500` 表示后端未配置 API Key；
- `502` 表示 DeepSeek API 调用失败。

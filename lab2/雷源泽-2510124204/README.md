# AI 聊天 Web 应用

一个使用原生 HTML、CSS、JavaScript 和 Python Flask 构建的 AI 聊天 Web 应用。前端通过 `fetch()` 调用本项目 Flask API，Flask 后端再调用 DeepSeek API。浏览器不会接触 DeepSeek API Key。

## 功能

- 创建、查看、修改和删除聊天消息。
- 使用 DeepSeek 生成真实 AI 回复。
- 将聊天记录保存到 JSON 文件，Flask 重启后仍可恢复。
- 创建、切换、重命名和删除多个聊天会话。
- 同一会话会携带最近 10 轮历史消息作为模型上下文。
- 所有确认、错误和状态反馈均显示在页面内，不使用浏览器弹窗。

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

`data/conversations.json` 是聊天记录持久化文件。`.env`、`.venv` 和 Python 缓存文件不会提交到 Git。

## 环境要求

- Python 3.9 或更高版本
- 可以访问 DeepSeek API 的网络环境
- DeepSeek API Key

## 安装依赖

在项目目录中使用 Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果默认 PyPI 镜像出现 SSL 或连接错误，可以改用：

```powershell
.\.venv\Scripts\python.exe -m pip install --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
```

## 配置 API Key

复制示例配置：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，写入真实 Key：

```dotenv
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已被 `.gitignore` 忽略。程序只在 Flask 后端读取 Key，不会把它返回给浏览器或写入日志。

可选环境变量：

```dotenv
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
```

程序默认使用 DeepSeek 当前的 `deepseek-flash` 模型，并关闭思考模式。

## 启动

```powershell
.\.venv\Scripts\python.exe app.py
```

服务启动后访问：

```text
http://localhost:5001/
```

按 `Ctrl+C` 停止服务。

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/hello` | 后端连通性测试 |
| `GET` | `/api/conversations` | 获取会话摘要列表 |
| `POST` | `/api/conversations` | 创建会话 |
| `GET` | `/api/conversations/<id>` | 获取会话及消息 |
| `PATCH` | `/api/conversations/<id>` | 修改会话名称 |
| `DELETE` | `/api/conversations/<id>` | 删除会话 |
| `POST` | `/api/conversations/<id>/messages` | 创建消息并生成 AI 回复 |
| `PATCH` | `/api/conversations/<id>/messages/<messageId>` | 修改消息 |
| `DELETE` | `/api/conversations/<id>/messages/<messageId>` | 删除消息 |

JSON 响应中的中文会直接显示，不会转义为 Unicode。

## API 测试

测试后端：

```powershell
curl.exe http://localhost:5001/api/hello
```

创建会话：

```powershell
curl.exe -X POST http://localhost:5001/api/conversations `
  -H "Content-Type: application/json" `
  -d "{}"
```

获取会话列表：

```powershell
curl.exe http://localhost:5001/api/conversations
```

向指定会话发送消息：

```powershell
curl.exe -X POST http://localhost:5001/api/conversations/1/messages `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"请用一句话介绍北京大学\"}"
```

## 数据结构与持久化

`data/conversations.json` 的最外层是数组，每个会话包含自己的消息数组：

```json
[
  {
    "id": 1,
    "title": "机器学习会话",
    "createdAt": "2026-09-27T10:00:00+00:00",
    "updatedAt": "2026-09-27T10:05:00+00:00",
    "messages": [
      {
        "id": 1,
        "message": "请用一句话介绍机器学习",
        "reply": "机器学习是让计算机从数据中自动学习规律的方法。",
        "createdAt": "2026-09-27T10:05:00+00:00"
      }
    ]
  }
]
```

创建、修改或删除数据后，Flask 会及时重写该文件。服务启动时会重新读取文件，因此重启后聊天记录仍然存在。写入时先写临时文件再替换正式文件，避免中途写入造成半个 JSON 文件。

## 多会话上下文

每次发送消息时，Flask 从当前会话中选取最近 10 轮历史，按顺序组装为：

```text
user -> assistant -> user -> assistant -> 当前 user 消息
```

这些内容一起发送给 DeepSeek。不同会话的数据相互独立，不会把另一个会话的历史传给当前模型请求。

## 选做功能

- 已完成 JSON 文件持久化。
- 已完成多会话及多轮对话上下文。

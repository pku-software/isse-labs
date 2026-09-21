# AI 聊天 Web 应用

## 项目简介

这是一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。前端通过 `fetch()` 请求 Flask API，后端使用本地环境变量中的 API Key 调用 DeepSeek，并以 JSON 格式向前端返回结果。

项目支持：

- 在浏览器中与 DeepSeek 进行问答；
- 创建、查看、修改和删除聊天记录；
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
│   └── messages.json
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

聊天记录的 JSON 格式为：

```json
{
  "id": 1,
  "message": "用户输入",
  "reply": "DeepSeek 回复"
}
```

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

## 数据存储

聊天记录持久化保存在 `data/messages.json` 中。文件最外层是 JSON 数组，每个元素是一条包含 `id`、`message` 和 `reply` 的聊天记录。

Flask 启动时读取该文件，创建、修改或删除记录后立即将完整数组写回文件，因此重启后仍能恢复数据。当前每条问答是独立记录，尚未启用多会话功能。

# AI 聊天 Web 应用

## 项目简介

这是一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。前端通过 `fetch()` 调用 Flask API，后端负责管理聊天记录、调用 DeepSeek API，并将数据持久化到 JSON 文件。

主要功能：

- 发送问题并获取 DeepSeek 生成的回复；
- 查看、修改和删除聊天记录；
- 在页面内完成编辑、删除确认和状态反馈；
- 使用 JSON 文件持久化数据，Flask 重启后仍可恢复记录。

## 环境要求

- Python 3.9 或更高版本；
- 可用的 DeepSeek API Key。

## 安装依赖

在项目目录中执行：

```bash
python -m pip install -r requirements.txt
```

## 配置

将 `.env.example` 复制为 `.env`，然后在 `.env` 中填入真实的 DeepSeek API Key：

```dotenv
DEEPSEEK_API_KEY=your_real_api_key
```

`.env` 已在 `.gitignore` 中忽略，不应提交到 Git。

## 启动

在项目目录中执行：

```bash
python app.py
```

服务启动后，在浏览器访问：

```text
http://localhost:5001/
```

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/hello` | 返回简单问候 |
| `POST` | `/api/messages` | 发送问题、调用 DeepSeek 并创建记录 |
| `GET` | `/api/messages` | 获取全部聊天记录 |
| `PATCH` | `/api/messages/<id>` | 修改指定记录的 `message` |
| `DELETE` | `/api/messages/<id>` | 删除指定记录 |

聊天记录格式：

```json
{
  "id": 1,
  "message": "用户输入",
  "reply": "DeepSeek 回复"
}
```

## API 测试

在 Flask 运行时，可使用 `curl` 创建一条记录：

```bash
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

## 数据持久化

聊天记录保存在 `data/messages.json` 中。文件最外层是 JSON 数组，每条记录是包含 `id`、`message` 和 `reply` 的 JSON 对象。创建、修改或删除记录后，后端会立即将最新数据写回该文件；Flask 启动时会读取它，因此记录可以跨重启保留。

## 选做功能

已完成 JSON 文件持久化。本项目未实现多会话功能。

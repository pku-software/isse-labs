# AI Chat Web Application

一个基于 Flask、HTML、CSS 和 JavaScript 构建的 AI 聊天 Web 应用。浏览器通过本地 Flask API 创建、读取、修改和删除聊天记录；Flask 在服务端调用 DeepSeek API 获取回复。

## 功能

- 发送消息并显示 DeepSeek 的真实回复；
- 查看、修改和删除聊天记录；
- 页面内显示编辑、删除确认、错误和状态反馈；
- 使用 `data/messages.json` 持久化聊天记录，重启 Flask 后自动恢复；
- API Key 仅保存在本地 `.env`，不会发送到浏览器。

## 安装依赖

在项目根目录运行：

```powershell
python -m pip install -r requirements.txt
```

## 配置 DeepSeek API Key

根据 `.env.example` 在项目根目录创建本地 `.env`，并填写自己的 Key：

```text
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已被 Git 忽略。不要将真实 Key 写入源代码、提交记录或公开内容。

## 启动应用

```powershell
python app.py
```

打开浏览器访问：<http://localhost:5001/>

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/hello` | 返回简单问候 JSON。 |
| `GET` | `/api/messages` | 获取全部聊天记录。 |
| `POST` | `/api/messages` | 创建记录并请求 DeepSeek 回复。 |
| `PATCH` | `/api/messages/<id>` | 修改指定记录的 `message`。 |
| `DELETE` | `/api/messages/<id>` | 删除指定记录。 |

创建或修改消息时，请使用 JSON 请求体：

```json
{"message":"你好"}
```

## API 测试示例

服务运行后，可在 PowerShell 中创建一条记录：

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/api/messages" -Method Post -ContentType "application/json; charset=utf-8" -Body '{"message":"请用一句话介绍北京大学"}'
```

## JSON 持久化

聊天记录保存在 `data/messages.json`。文件最外层是一个数组，每项为包含 `id`、`message` 和 `reply` 的对象。Flask 启动时读取该文件，并在创建、修改或删除记录后立即写回。

## 选做功能

已完成 JSON 文件持久化；未实现多会话与多轮上下文。

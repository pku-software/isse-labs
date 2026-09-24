# AI 聊天 Web 应用

## 项目简介

这是一个使用 HTML、CSS、JavaScript 与 Flask 构建的 AI 聊天 Web 应用。前端通过 RESTful API 创建、读取、修改和删除聊天记录，Flask 后端调用 DeepSeek API 生成回复。

聊天记录保存在 Flask 进程的内存中，服务重启后会清空。本项目未实现 JSON 持久化和多会话选做功能。

## 功能

- 由 Flask 同时提供前端页面和后端 API；
- 使用 `fetch()` 与相对 URL 完成前后端通信；
- 以一次问答为一条记录，实现 Create、Read、Update、Delete；
- 通过 DeepSeek `deepseek-flash` 模型生成真实回复；
- API Key 只由后端从 `.env` 读取；
- 编辑、删除确认、成功和错误反馈均显示在页面内。

## 安装依赖

建议使用 Python 虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 配置 API Key

从示例文件创建本地配置：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，将占位值替换为自己的 DeepSeek API Key：

```dotenv
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 已被 `.gitignore` 忽略，不应提交到 Git；`.env.example` 只能保留示例值。

## 启动应用

在本项目目录中运行：

```powershell
python app.py
```

浏览器访问：

```text
http://localhost:5001/
```

## API

| 方法 | 路径 | 说明 | 请求体 |
|---|---|---|---|
| `GET` | `/api/hello` | 返回中文问候 | 无 |
| `POST` | `/api/messages` | 调用 DeepSeek 并创建问答记录 | `{"message":"用户输入"}` |
| `GET` | `/api/messages` | 获取全部聊天记录 | 无 |
| `PATCH` | `/api/messages/<id>` | 修改指定记录的用户消息 | `{"message":"修改后的输入"}` |
| `DELETE` | `/api/messages/<id>` | 删除指定记录 | 无 |

一条聊天记录的结构如下：

```json
{
  "id": 1,
  "message": "用户输入",
  "reply": "模型回复"
}
```

## 简单 API 测试

启动 Flask 后，可在另一个 PowerShell 终端中测试：

```powershell
curl.exe http://localhost:5001/api/hello
curl.exe -X POST "http://localhost:5001/api/messages" -H "Content-Type: application/json" --data-raw '{\"message\":\"请用一句话介绍北京大学\"}'
```

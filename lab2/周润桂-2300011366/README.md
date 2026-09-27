# AI 聊天 Web 应用

基于 HTML、CSS、JavaScript 和 Flask 的聊天应用。前端通过后端 API 管理聊天记录，后端调用 DeepSeek 生成回复。

## 功能

- 在同一个 Flask 服务中提供网页和 JSON API。
- 创建、查看、修改和删除单条问答记录；发送消息时由 DeepSeek 生成回复。
- 每次问答互相独立；修改提问不会重新生成已有回复。
- 记录只保存在 Flask 进程内存中，重启服务后清空；没有 JSON 持久化或多会话功能。

## 安装与配置

建议使用 Python 3.11。在本目录运行：

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

随后自行编辑 `.env`，将 `DEEPSEEK_API_KEY` 的示例值替换成自己的 Key。`.env` 已由本目录的 `.gitignore` 排除，不要提交或分享它。

## 启动与访问

在本目录运行：

```powershell
python app.py
```

浏览器访问 `http://localhost:5001/`。前端通过相对路径请求同一 Flask 服务的 API。

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/api/hello` | 返回 `{"message":"你好"}` |
| GET | `/api/messages` | 返回全部问答记录 |
| POST | `/api/messages` | 以 `{"message":"问题"}` 创建记录并生成回复 |
| PATCH | `/api/messages/<id>` | 以 `{"message":"新问题"}` 修改提问 |
| DELETE | `/api/messages/<id>` | 删除记录，成功时返回 204 |

一条记录的格式为 `{"id":1,"message":"问题","reply":"模型回复"}`。缺少有效的 `message` 返回 400，找不到 ID 返回 404；Key 缺失或模型请求失败时返回 JSON 错误。

## 验证方法

服务运行后，可以先在另一个 PowerShell 终端测试问候接口：

```powershell
curl.exe http://localhost:5001/api/hello
```

再用 PowerShell 发送 JSON 请求：

```powershell
Invoke-RestMethod -Uri 'http://localhost:5001/api/messages' -Method Post -ContentType 'application/json; charset=utf-8' -Body (@{ message = '用一句话介绍北京大学' } | ConvertTo-Json -Compress)
```

响应应包含 `id`、`message` 和模型生成的 `reply`。浏览器中可继续验证查看、修改和删除。

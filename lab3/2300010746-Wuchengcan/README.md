# AI 聊天 Web 应用

在浏览器中使用的聊天应用。前端页面通过 Flask API 收发消息，后端调用 DeepSeek 生成回复。API Key 只保存在后端的 `.env` 中。

一条聊天记录的形状为：

```json
{"id": 1, "message": "用户输入", "reply": "模型回复"}
```

记录保存在当前 Python 进程的内存中。Flask 重启后，这些记录会清空。

## 项目功能

- 浏览器中发送消息，并显示用户内容和模型回复
- 打开页面时加载当前进程中的全部记录
- 修改或删除一条记录，操作后页面立即更新
- `GET /api/hello` 用于检查服务是否可用

## 安装依赖

在个人项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 配置

复制示例文件并填写自己的 Key：

```powershell
copy .env.example .env
```

`.env` 中只保留一行，把占位符换成真实 Key：

```text
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 已被 `.gitignore` 忽略，不要把真实 Key 写入代码或提交到 Git。

## 启动

```powershell
.\.venv\Scripts\python.exe app.py
```

Flask 监听 `5001` 端口。保持这个终端运行。

## 访问地址

http://localhost:5001/

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 返回前端页面 |
| GET | `/api/hello` | 返回 `{"message":"你好"}` |
| GET | `/api/messages` | 返回全部聊天记录 |
| POST | `/api/messages` | 创建记录。请求体为 `{"message":"用户输入"}`，`reply` 为 DeepSeek 返回的文本 |
| PATCH | `/api/messages/<id>` | 修改指定记录的 `message` |
| DELETE | `/api/messages/<id>` | 删除指定记录 |

缺少 `message`、内容为空或 `id` 不存在时，接口返回 JSON 错误和对应的 HTTP 状态码。Key 缺失或模型调用失败时同样返回 JSON 错误。

## API 测试

服务启动后，在另一个终端执行。

检查服务：

```powershell
curl.exe http://localhost:5001/api/hello
```

发送一条消息：

```powershell
curl.exe -X POST http://localhost:5001/api/messages -H "Content-Type: application/json" -d '{"message":"请用一句话介绍北京大学"}'
```

返回中应包含 `id`、`message` 和模型生成的 `reply`，且不包含 API Key。

## 选做功能

未实现 JSON 文件持久化，也未实现多个聊天会话。

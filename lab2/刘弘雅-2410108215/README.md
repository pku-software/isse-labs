# AI 聊天 Web 应用

一个基于 Flask 与原生 HTML、CSS、JavaScript 构建的 AI 聊天 Web 应用。前端通过 `fetch()` 调用后端 API，后端接入 DeepSeek 生成回复，并把聊天记录持久化到 JSON 文件。

## 项目功能

- 提供聊天页面，可输入消息并发送；
- 创建、查看、修改和删除聊天记录；
- 通过 Flask 后端调用 DeepSeek 获得真实模型回复；
- 将聊天记录持久化到本地 JSON 文件，Flask 重启后仍可恢复。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 API Key

1. 根据示例文件创建本地配置：

```bash
Copy-Item .env.example .env
```

2. 在 `.env` 中填写真实 Key：

```text
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已被 `.gitignore` 忽略，不要提交到 Git。

## 启动 Flask

```bash
python app.py
```

启动后浏览器访问：

```text
http://localhost:5001/
```

## API 设计

- `GET /api/hello`：返回 `{"message":"你好"}`；
- `GET /api/messages`：返回全部聊天记录；
- `POST /api/messages`：创建记录，请求体为 `{"message":"用户输入"}`；
- `PATCH /api/messages/<id>`：修改指定记录，请求体为 `{"message":"新内容"}`；
- `DELETE /api/messages/<id>`：删除指定记录。

每条记录的结构为：

```json
{
  "id": 1,
  "message": "用户输入",
  "reply": "模型回复"
}
```

## 最简单的 API 测试

```bash
curl.exe -X POST http://localhost:5001/api/messages -H "Content-Type: application/json" -d '{"message":"请用一句话介绍北京大学"}'
```

也可以使用 PowerShell：

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:5001/api/messages' -ContentType 'application/json; charset=utf-8' -Body '{"message":"请用一句话介绍北京大学"}'
```

## 数据持久化

聊天记录保存在 `data/messages.json` 中，最外层是一个数组，每个元素包含 `id`、`message` 和 `reply`。

## 选做功能

- JSON 文件持久化：已实现。

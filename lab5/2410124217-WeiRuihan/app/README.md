# AI 聊天 Web 应用

这是一个使用 Flask、HTML、CSS 和 JavaScript 构建的 AI 聊天 Web 应用。前端通过 Flask API 创建、查看、修改和删除聊天记录；新消息由 Flask 调用 DeepSeek 生成回复。

## 功能

- 页面加载时读取当前 Flask 进程中的聊天记录；
- 支持创建、修改、删除聊天记录；
- 修改、删除确认和错误反馈都显示在页面内；
- DeepSeek API Key 只由后端读取，前端不会获取 Key；
- 聊天记录只保存在 Python 内存中，重启 Flask 后会清空。

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env`，再在 `.env` 中填写真实的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=your_real_api_key
```

`.env` 已被 Git 忽略，不应提交到仓库。

## 启动

```powershell
python app.py
```

服务运行在 `http://localhost:5001`。

## 浏览器访问

打开 <http://localhost:5001/>。

## API

- `GET /api/hello`：返回欢迎信息；
- `GET /api/messages`：获取全部聊天记录；
- `POST /api/messages`：创建消息并调用 DeepSeek；
- `PATCH /api/messages/<id>`：修改指定记录的 `message`；
- `DELETE /api/messages/<id>`：删除指定记录。

聊天记录格式如下：

```json
{"id": 1, "message": "用户输入", "reply": "模型回复"}
```

## API 测试

PowerShell 中可以执行：

```powershell
Invoke-RestMethod `
  -Uri 'http://localhost:5001/api/messages' `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"message":"请用一句话介绍北京大学"}'
```

## 选做功能

未实现 JSON 文件持久化和多会话功能。

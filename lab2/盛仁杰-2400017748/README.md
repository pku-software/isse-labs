# AI 聊天 Web 应用

## 项目说明

本项目使用 Flask、HTML、CSS 和 JavaScript 构建一个 AI 聊天 Web 应用。

## 安装与运行

```bash
conda activate isse-lab2
python -m pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:5001/`。

## 配置

复制 `.env.example` 为 `.env`，填入 `DEEPSEEK_API_KEY`。`.env` 不应提交到 Git。

聊天记录保存在 `data/messages.json`，应用启动时会自动加载。

## API

- `GET /api/hello`：检查服务是否运行。
- `POST /api/messages`：创建一条聊天记录。
- `GET /api/messages`：读取全部聊天记录。
- `PATCH /api/messages/<id>`：修改聊天消息。
- `DELETE /api/messages/<id>`：删除聊天记录。

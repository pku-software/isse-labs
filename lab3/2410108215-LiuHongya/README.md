# Lab 3：AI 聊天应用容器化部署

延续 Lab 2 的 HTML/CSS/JavaScript + Flask + DeepSeek 聊天应用，把它打包成镜像并在云端构建、运行。

## 项目结构

```text
.
├── app.py              # Flask 后端：页面、静态资源、聊天 API
├── frontend/           # 原生前端：index.html、app.js、style.css
├── requirements.txt    # Python 依赖（含 Gunicorn）
├── Dockerfile          # 构建镜像的说明
├── .dockerignore       # 构建时排除的文件
├── .gitignore          # Git 忽略规则
└── .env.example        # 环境变量示例（无真实值）
```

## 后端如何读取 Key

后端在运行时通过 `DEEPSEEK_API_KEY` 环境变量读取 DeepSeek Key，前端不接触 Key。真实 Key 由 ECI 容器运行时注入，不进源码、镜像或 GitHub。

## 本地运行（可选）

```bash
pip install -r requirements.txt
python app.py
```

启动后访问 `http://localhost:5001/`。

## Dockerfile 说明

- `FROM python:3.12-slim`：选择含 Python 的基础镜像；
- `WORKDIR /app`：设置容器内工作目录；
- `COPY requirements.txt .` 与 `RUN pip install ...`：先复制依赖清单并安装（含 Gunicorn）；
- `COPY app.py .`、`COPY frontend/ frontend/`：复制应用与前端；
- `EXPOSE 5001`：声明容器对外的端口；
- `CMD [...]`：用 Gunicorn 以单 worker 监听 `0.0.0.0:5001` 启动 Flask 应用。

## API 设计

- `GET /api/hello`：健康检查；
- `GET /api/messages`：查看全部聊天记录；
- `POST /api/messages`：发送消息并获得模型回复；
- `PATCH /api/messages/<id>`：修改记录；
- `DELETE /api/messages/<id>`：删除记录。
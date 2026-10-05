# Lab 3：ACR 构建与 ECI 部署

本项目由 Lab 2 的 Flask + DeepSeek 聊天应用迁移而来。

## 目录结构

- `app.py`：Flask 后端，提供页面、静态资源和聊天 API。
- `frontend/`：HTML、CSS 和 JavaScript 前端。
- `requirements.txt`：Python 依赖。
- `Dockerfile`：容器构建说明。

## 本地运行

先安装依赖并设置 `DEEPSEEK_API_KEY`，再运行：

```bash
python app.py
```

浏览器访问 `http://127.0.0.1:5001/`。

## 容器运行

镜像由阿里云 ACR 从 GitHub 个人分支云端构建，运行命令由 `Dockerfile` 中的 Gunicorn 启动，监听 `0.0.0.0:5001`。

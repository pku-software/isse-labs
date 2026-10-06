# Lab 3 Flask 聊天应用

本目录基于 Lab 2 的 Flask + HTML/CSS/JavaScript 聊天应用。Flask 提供页面、静态资源和 `/api/messages` 聊天记录接口；创建消息时，后端在运行时读取 `DEEPSEEK_API_KEY` 并请求 DeepSeek。

## 容器化

Dockerfile 使用 `python:3.12-slim`，在 `/app` 中先复制并安装 `requirements.txt`，再复制应用源码和前端。容器运行时由单 worker 的 Gunicorn 在 `0.0.0.0:5001` 启动 `app:app`；`EXPOSE 5001` 说明应用使用该端口。

`.dockerignore` 排除 `.env`、虚拟环境、Python 缓存、本地 Git 元数据、实验轨迹和截图，避免它们进入镜像构建上下文。真实 Key 不写入代码、Dockerfile、镜像或 Git 仓库；仅在 ECI 的容器运行时环境变量中设置。

## 云端部署记录

- ACR 地域：华北 2（北京）
- ACR 私有镜像仓库：`isse-lab3/lab3-chat`
- ACR 构建分支：`lab3/2410124217-WeiRuihan`
- ACR 构建上下文：`/lab3/2410124217-WeiRuihan/`
- Dockerfile：`Dockerfile`
- 镜像标签：`lab3-e9e1e7c`
- 自动构建：关闭；海外机器构建：开启
- ECI 地域与算力类别：华北 2（北京），经济型
- ECI 容器端口：`5001/TCP`；安全组仅临时放行 `5001/TCP`
- ECI 环境变量：仅在运行时配置 `DEEPSEEK_API_KEY`，不写入镜像、Git 或截图
- 公网访问：`http://39.105.106.202:5001/`
- 验证：外部 HTTP 请求已验证页面、静态资源、`/api/hello` 和 `/api/messages`；浏览器实际完成了非敏感聊天与 CRUD 验证
- 风险与清理：该演示使用未加密 HTTP，聊天 API 没有鉴权。完成 PR 后立即删除 ECI，并检查和释放只为本实验创建的 EIP。

`screenshots/` 包含 `eci-created.png`（ECI 创建成功）和 `public-page.png`（浏览器公网访问）；`AGENT_TRACE.md` 将在最后保存本次真实 Codex 对话轨迹或分享链接。

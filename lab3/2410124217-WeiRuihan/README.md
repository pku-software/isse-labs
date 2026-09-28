# Lab 3 Flask 聊天应用

本目录基于 Lab 2 的 Flask + HTML/CSS/JavaScript 聊天应用。Flask 提供页面、静态资源和 `/api/messages` 聊天记录接口；创建消息时，后端在运行时读取 `DEEPSEEK_API_KEY` 并请求 DeepSeek。

## 容器化

Dockerfile 使用 `python:3.12-slim`，在 `/app` 中先复制并安装 `requirements.txt`，再复制应用源码和前端。容器运行时由单 worker 的 Gunicorn 在 `0.0.0.0:5001` 启动 `app:app`；`EXPOSE 5001` 说明应用使用该端口。

`.dockerignore` 排除 `.env`、虚拟环境、Python 缓存、本地 Git 元数据、实验轨迹和截图，避免它们进入镜像构建上下文。真实 Key 不写入代码、Dockerfile、镜像或 Git 仓库；仅在 ECI 的容器运行时环境变量中设置。

## 云端部署记录

- ACR 地域：待配置（计划使用华北 2，北京）
- ACR 构建分支：`lab3/2410124217-WeiRuihan`
- ACR 构建上下文：`/lab3/2410124217-WeiRuihan/`
- 镜像标签：待 ACR 构建后填写
- ECI 规格、公网地址与访问验证：待部署后填写

本实验完成后，`screenshots/` 将保存 ECI 创建成功和浏览器公网访问的两张原始截图；`AGENT_TRACE.md` 将保存本次真实 Codex 对话轨迹或分享链接。

# Lab 3：AI 聊天应用容器化与云端部署

## 项目说明

本项目迁移自 Lab 2。Flask 同时提供前端页面、静态资源和 REST API，前端使用同源相对路径调用 API，后端调用 DeepSeek 生成回复。聊天记录保存在进程内存中，容器重启后会清空。

## 容器配置

- 基础镜像：`python:3.12-slim`
- 应用服务器：Gunicorn，单 worker
- 监听地址：`0.0.0.0:5001`
- WSGI 入口：`app:app`
- 运行时环境变量：`DEEPSEEK_API_KEY`

镜像构建时不会写入真实 Key。`.dockerignore` 排除了本地 `.env`、虚拟环境、缓存、对话轨迹和截图等不需要进入镜像的内容。

## 本地开发运行

在 PowerShell 中安装依赖并启动 Flask 开发服务器：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

在 `.env` 中设置本地实验 Key 后，访问 `http://localhost:5001/`。`.env` 不得提交到 Git。

## ACR 云端构建

- 地域：待完成 ACR 配置后记录
- GitHub 仓库：个人 Fork `isse-labs`
- 构建分支：`lab3/2300011735-fengsishan`
- 构建上下文：`/lab3/2300011735-fengsishan/`
- Dockerfile：`Dockerfile`
- 镜像标签：待构建时记录

## ECI 部署与验证

ECI 地域、镜像地址、实例规格、公网访问方式和验证结果将在实际部署后补充。容器运行时仅设置环境变量名称 `DEEPSEEK_API_KEY`，真实值不写入本文档。

## 清理计划

公网验证和 PR 提交完成后，删除本实验创建的 ECI，并检查关联 EIP 是否仍作为独立资源计费。

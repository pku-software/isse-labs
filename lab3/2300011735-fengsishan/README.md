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

- 地域：华北 2（北京）
- GitHub 仓库：个人 Fork `SishanFeng/isse-labs`
- 构建分支：`lab3/2300011735-fengsishan`
- 构建上下文：`/lab3/2300011735-fengsishan/`
- Dockerfile：`Dockerfile`
- ACR 仓库：私有仓库 `lab3-chat-2300011735`
- 镜像标签：`lab3-0a714fe`
- 构建方式：开启海外机器构建，由学生手动触发

ACR 已成功从上述个人分支完成云端构建。后续若修改代码，需要先将新 Commit Push 到个人 Fork，再用新的版本标签重新触发构建。

## ECI 部署与验证

- 地域与可用区：华北 2（北京），可用区 H
- 容器组名称：`lab3-2300011735`
- 算力类别与规格：经济型，0.25 vCPU、512 MiB
- ACR 仓库与镜像标签：`lab3-chat-2300011735:lab3-0a714fe`
- 应用监听端口：Gunicorn 监听 `0.0.0.0:5001`
- 运行时环境变量名称：`DEEPSEEK_API_KEY`，真实值不进入 Git、镜像或本文档
- 公网入口：自动创建并绑定 EIP，验证地址为 `http://123.57.161.37:5001/`
- 安全组：入方向允许 TCP `5001/5001`，仅用于本次短时实验

实际验证结果：浏览器页面和静态资源成功加载，前端显示 API 已连接；`GET /api/hello` 返回 HTTP 200；学生使用非敏感内容收到过一次模型回复，并验证了聊天记录的创建、读取、修改和删除。两张原始验证截图保存在 `screenshots/`。

本实验公网入口使用 HTTP，聊天内容未加密；聊天 API 没有鉴权，知道地址的人可能操作聊天记录、调用模型并产生费用。该部署只用于短时教学演示，不是正式服务的安全方案。

## 清理计划

PR 提交完成后，删除本实验创建的 ECI，并检查关联 EIP 是否仍作为独立资源计费。随后建议废除本次实验使用的 Key。

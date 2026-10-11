# Lab 3：将 Flask 聊天应用部署到云端

姓名：李彰宇
学号：2500013086

## 项目说明

本项目沿用 Lab 2 的 HTML、CSS、JavaScript 与 Flask 聊天应用。Flask 在同一服务中提供网页、静态资源和会话 API；前端通过同源相对路径访问 API。应用运行时从后端环境变量 `DEEPSEEK_API_KEY` 读取实验 Key，真实 Key 不进入源码、镜像或 Git 仓库。

会话数据只保存在容器本地文件中，本实验不配置云端持久化存储。

## 容器运行

ACR 根据本目录的 `Dockerfile` 在云端构建镜像。容器启动时由 Gunicorn 使用单 worker 在 `0.0.0.0:5001` 监听请求，并加载 `app.py` 中的 Flask `app` 对象。

## ACR 构建记录

ACR 个人版与后续 ECI 均使用华北 2（北京）地域。

- ACR 镜像命名空间：`lab3-chat`
- ACR 镜像仓库：`lab3-chat`
- GitHub 代码仓库：个人 Fork `lzy796/isse-labs`
- 构建分支：`lab3/2500013086-LiZhangyu`
- 构建上下文：`/lab3/2500013086-LiZhangyu/`
- Dockerfile：个人目录中的 `Dockerfile`
- 镜像标签：`lab3-4725134`
- 构建方式：关闭自动构建，使用海外机器云端手动构建

ACR 已成功从上述个人 GitHub 分支构建并保存镜像。本地代码更新后，需要先提交并 Push 到该个人分支，再触发新的 ACR 构建。

## ECI 配置与访问验证

完成 ECI 部署和公网访问验证后补充。

## 安全与清理

真实 Key 仅在 ECI 运行时通过环境变量设置。完成实验、提交 PR 后，将删除本实验创建的 ECI，并核对相关 EIP 等计费资源是否仍然存在。

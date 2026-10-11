# Lab 3：ACR 构建与 ECI 部署

## 项目说明

本项目迁移自 Lab 2，是一个由 HTML、CSS、JavaScript 和 Flask 构成的 DeepSeek 聊天应用。Flask 同时提供前端页面、静态资源和聊天记录 API；前端通过同源相对路径访问 API。

真实 `DEEPSEEK_API_KEY` 只在容器运行时通过环境变量提供，不写入源码、Dockerfile、镜像或仓库。聊天记录写入容器内的 `data/messages.json`，本实验不要求云端持久化。

## 容器配置

- 基础镜像：`python:3.12-slim`
- 服务进程：Gunicorn，单 worker
- 监听地址：`0.0.0.0:5001`
- 应用入口：`app:app`
- 构建上下文：本目录

## ACR 构建

- 地域：华北 2（北京）
- ACR 命名空间：`suyingrui-lab3`
- 私有镜像仓库：`lab3-chat`
- GitHub 代码源：`suyingrui2024/isse-labs`
- 构建分支：`lab3/2310306221-suyingrui`
- 构建上下文：`/lab3/2310306221-suyingrui/`
- Dockerfile：`Dockerfile`
- 镜像标签：`lab3-ea7db05`
- 构建方式：关闭自动构建，手动触发 ACR 云端构建

本地代码更新后，需要先 Commit 并 Push 到上述个人 GitHub 分支，再触发新的 ACR 构建并使用新的镜像标签。

## ECI 部署与验证

- 地域：华北 2（北京），北京可用区 H
- 实例类型：按量付费普通实例
- 算力类别与规格：经济型，1 vCPU、2 GiB 内存
- 镜像：`suyingrui-lab3/lab3-chat:lab3-ea7db05`
- 容器启动方式：沿用 Dockerfile 的 Gunicorn `CMD`
- 应用端口：`5001/TCP`
- 运行时环境变量名称：`DEEPSEEK_API_KEY`（真实值不进入仓库、截图或文档）
- 公网访问方式：自动创建并绑定 EIP，使用 `http://60.205.177.216:5001/` 进行短时实验验证
- 安全组：入方向临时允许公网访问 `5001/TCP`

已验证首页与 CSS 静态资源正常加载，`/api/hello` 和 `/api/messages` 返回 HTTP 200；学生浏览器完成了一次非敏感模型回复，以及聊天记录的读取、修改和删除。验证截图位于 `screenshots/eci-created.png` 与 `screenshots/public-page.png`。

本实验公网入口使用 HTTP，聊天内容未加密；聊天 API 没有鉴权，其他人可能读取或改动共享记录、调用模型并消耗额度。该配置只用于短时教学演示，不作为正式服务部署方案。

## 清理计划

提交 PR 后立即删除本实验创建的 ECI，并检查自动创建的 EIP 或其他公网计费资源是否仍然独立存在；仅停止浏览器访问不会停止计费。实验 Key 随后建议废除。

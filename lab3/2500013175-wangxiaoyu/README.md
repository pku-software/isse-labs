# Lab 3：AI 聊天应用容器化与云端部署

## 项目概述

本项目沿用 Lab 2 的 HTML/CSS/JavaScript + Flask + DeepSeek 聊天应用。Flask 同时提供前端页面、静态资源和会话 API，前端使用同源相对路径访问 API。

DeepSeek API Key 只由后端在运行时从 `DEEPSEEK_API_KEY` 环境变量读取。真实 Key 不应写入源码、Dockerfile、镜像、Git 或构建参数。

## 容器配置

- 基础镜像：`python:3.12-slim`
- 应用入口：`app:app`
- Web 服务器：Gunicorn，单 worker
- 监听地址：`0.0.0.0:5001`
- 页面、静态资源和 API 由同一个 Flask 容器提供

Lab 2 中的 JSON 会话数据没有迁移。本 Lab 不要求云端持久化，容器重建或删除后，运行期间产生的会话数据可能丢失。

## ACR 构建记录

- 地域：华北 2（北京）
- 代码源：个人 GitHub Fork `foolyuyu/isse-labs`
- GitHub 分支：`lab3/2500013175-wangxiaoyu`
- 构建上下文：`/lab3/2500013175-wangxiaoyu/`
- Dockerfile 路径：`/lab3/2500013175-wangxiaoyu/Dockerfile`
- ACR 命名空间：`isse`
- 私有镜像仓库：`lab3-chat`
- 镜像版本标签：`lab3-3da9592`
- 构建方式：ACR 云端手动构建，已构建成功

## ECI 部署与验证

- 地域：华北 2（北京），与 ACR 同地域
- 容器组名称：`lab3-2500013175`
- 算力类别：经济型
- 规格：0.25 vCPU、512 MiB
- 镜像：ACR 私有仓库 `isse/lab3-chat:lab3-3da9592`
- 应用端口：`5001`
- 运行时环境变量名称：`DEEPSEEK_API_KEY`
- 公网地址：`http://39.106.113.130:5001/`

已通过公网验证首页、CSS、JavaScript、`/api/hello` 和会话 API 可访问。学生使用电脑浏览器完成会话 CRUD 和非敏感内容的模型回复验证，并使用手机访问同一公网服务。

必交验证截图：

- `screenshots/eci-created.png`：ECI 容器组已创建且处于运行中。
- `screenshots/public-page.png`：电脑浏览器地址栏包含本次公网 IP 和端口，页面已加载并获得模型回复。

## 安全与资源清理

本 Lab 使用短时公网 HTTP 演示，聊天内容未加密；公开 API 也没有鉴权，他人可能访问并消耗模型额度。因此不应输入敏感信息，也不应将该方案直接用于正式服务。

PR 提交后将删除本 Lab 创建的 ECI，并检查自动创建的 EIP 是否仍独立存在和计费。建议在实验结束后废除本次使用的 Key。

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

完成 ACR 构建后补充地域、仓库、分支、构建上下文和镜像标签。

## ECI 部署与验证

完成 ECI 部署后补充实例配置、运行时环境变量名称和访问验证结果。

## 清理计划

提交 PR 后删除本实验创建的 ECI，并检查关联的 EIP 或其他公网计费资源是否仍然存在。

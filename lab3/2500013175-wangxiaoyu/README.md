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

- 地域：待构建时补充
- GitHub 分支：`lab3/2500013175-wangxiaoyu`
- 构建上下文：`/lab3/2500013175-wangxiaoyu/`
- Dockerfile：`Dockerfile`
- 镜像仓库与版本标签：待构建时补充

## ECI 部署与验证

待 ECI 创建和公网访问完成后补充。

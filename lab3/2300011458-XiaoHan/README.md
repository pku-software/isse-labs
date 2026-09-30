# Lab 3：Flask 聊天应用容器化与云端部署

## 项目来源

本项目由 Lab 2 的多会话聊天应用迁移而来。前端使用 HTML、CSS 和 JavaScript，后端使用 Flask，并通过 OpenAI 兼容客户端调用 DeepSeek API。

## 应用结构

- Flask 在根路径提供前端页面和静态资源。
- 前端通过同源相对路径访问会话与消息 API。
- 后端从运行时环境变量 DEEPSEEK_API_KEY 读取实验 Key。
- 会话和消息支持创建、查询、修改和删除。
- 本实验不要求云端持久化，运行时产生的会话数据不提交到 Git。

## 容器配置

- 基础镜像：python:3.12-slim
- 工作目录：/app
- 服务程序：Gunicorn
- Worker 数量：1
- 监听地址：0.0.0.0:5001
- Flask 入口：app:app

构建镜像时先复制 requirements.txt 并安装依赖，再复制应用源码，使只修改源码时有机会复用依赖安装步骤的构建缓存。

.dockerignore 会排除本地环境变量、虚拟环境、Python 缓存、真实聊天数据、实验对话轨迹、截图和项目说明，避免这些内容进入镜像构建上下文。

## ACR 云端构建

- 地域：华北 2（北京）
- 仓库：`lab3-xiaohan`（私有）
- GitHub 代码仓库：`Xiao-Han666/isse-labs`
- 构建分支：`lab3/2300011458-XiaoHan`
- 构建上下文：`/lab3/2300011458-XiaoHan/`
- Dockerfile：构建上下文中的 `Dockerfile`
- 镜像标签：`lab3-10230ba`
- 构建方式：关闭自动构建，由 ACR 手动触发云端构建

ACR 构建成功后将镜像保存在私有镜像仓库中，后续由同地域的 ECI 选择并运行该镜像。

## ECI 部署与验证

将在完成 ECI 部署后补充实例配置、公网访问方式和验证结论。实验 Key 只在容器运行时通过环境变量设置，不写入源码、Dockerfile 或镜像。

## 清理计划

完成公网验证和 PR 后，删除本实验创建的 ECI，并检查关联的 EIP 等计费资源是否仍然存在。

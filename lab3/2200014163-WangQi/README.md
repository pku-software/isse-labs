# Lab 3：王琪（2200014163）—— 从代码到云端

本目录是 Lab 3 的个人提交目录，延续 Lab 2 的 HTML/CSS/JavaScript + Flask + DeepSeek 聊天应用，并将其容器化后交由阿里云 ACR 构建、ECI 运行。

## 项目架构

- 后端：Flask，同时提供页面（`frontend/` 静态资源）、`/api/*` 接口和 `/api/hello` 健康检查。
- 前端：原生 HTML/CSS/JS，用同源相对路径 `fetch()` 调用后端，不写死主机地址。
- Key 处理：后端通过 `DEEPSEEK_API_KEY` 环境变量读取，运行时由 ECI 注入；前端不接触 Key，`.env` 不入库、不入镜像。
- 数据：会话与消息暂存于容器内的 `data/conversations.json`，本 Lab 不要求云端持久化。

## Dockerfile 关键配置

- 基础镜像：`python:3.11-slim`
- 工作目录：`/app`
- 先复制 `requirements.txt` 并安装依赖（含 `gunicorn`），再复制源码，以利用构建层缓存
- 启动：Gunicorn 单 worker，监听 `0.0.0.0:5001`，入口 `app:app`
- `EXPOSE 5001` 仅为端口声明；真正监听端口由 Gunicorn 的 `--bind` 决定
- `.dockerignore` 排除 `.env`、缓存、`data/`、`.git/`、轨迹与截图

## ACR 云端构建

- 地域：华北 2（北京）
- 代码源：个人 GitHub Fork `QiWang3569/isse-labs`
- 分支：`lab3/2200014163-WangQi`
- 构建上下文目录：`/lab3/2200014163-WangQi/`
- 镜像标签：`lab3-f1b949b`
- 镜像仓库 / 完整镜像地址：（待 ECI 选择镜像时补记）

## 部署与验证

（待 ECI 创建并访问后补记）

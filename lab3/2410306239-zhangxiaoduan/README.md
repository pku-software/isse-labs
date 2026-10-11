# Lab 3：聊天应用云端部署

**姓名**：张效端　**学号**：2410306239

## 项目来源与架构

- 代码来自 Lab 2 的 Flask 聊天应用（`app.py` + `frontend/`），本 Lab 不修改应用逻辑，只负责部署。
- 架构：浏览器 → 公网 IP:5001 → ECI 容器 → Gunicorn → Flask → DeepSeek API。
- 依赖（requirements.txt）：flask、python-dotenv、openai、gunicorn。

## Dockerfile 关键配置

- 基础镜像：`python:3.11-slim`。
- 先 `COPY requirements.txt` 并安装依赖，再 `COPY` 源码——利用 Docker 分层缓存，改代码时不必重装依赖。
- `EXPOSE 5001` 仅为文档性元数据，实际监听端口由启动命令决定。
- 启动命令：`gunicorn --bind 0.0.0.0:5001 --workers 1 app:app`（单 worker 足以支撑本实验，且配合内存态会话数据）。

## ACR 云构建

- 地域：华北2（北京），个人版实例。
- 仓库：`zhangxiaoduan/lab3`（私有）。
- 代码源：GitHub 仓库 `xiaoduan-168/isse-labs`。
- 构建分支：`lab3/2410306239-zhangxiaoduan`。
- 构建上下文：`/lab3/2410306239-zhangxiaoduan/`。
- 镜像标签：`lab3-6183a2d`。
- 自动构建：关闭（按需手动触发，文档改动无需重新构建）。
- 镜像完整地址形如：`registry.cn-beijing.aliyuncs.com/zhangxiaoduan/lab3:lab3-6183a2d`。

## ECI 配置

（待任务 3 填写：实例规格、端口、环境变量名称）

## 公网访问验证

（待任务 4 填写：访问方式与验证结论）

## 安全风险与清理计划

（待任务 5 填写：无鉴权风险说明与资源清理计划）

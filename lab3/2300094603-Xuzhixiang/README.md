# Lab 3：许智翔 2300094603

## 项目与架构

沿用本人 Lab 2 的 Flask + HTML/CSS/JavaScript 聊天应用，保留聊天记录的新增、查看、修改、删除及后端 DeepSeek 调用。Flask 提供首页、`/static/` 静态资源与 `/api/messages` API，前端使用同源相对路径。

GitHub 个人 Fork 保存源码；ACR 从个人分支云端构建并保存镜像；ECI 拉取镜像运行；容器内由 Gunicorn 启动 Flask。无需本地安装 Docker。

## Dockerfile 配置

- 基础环境：`python:3.12-slim`，工作目录 `/app`。
- 先复制 `requirements.txt` 并安装依赖，再复制 `app.py` 和 `frontend/`，便于构建器在仅源码变化时复用依赖层缓存。
- Gunicorn 入口为 `app:app`，单 worker 监听 `0.0.0.0:5001`，请求超时 90 秒，为后端最多 60 秒的模型请求留出余量。
- `EXPOSE 5001` 只声明预期端口，不会自动开放公网访问。
- `.dockerignore` 排除 `.env`、虚拟环境、缓存、聊天数据、截图和对话轨迹；Dockerfile 只复制运行所需文件。
- 构建失败后需要修复并重新触发；未变化的步骤可能复用缓存，ACR 不保证断点续跑。

## 运行时配置与数据

由学生在 ECI 容器运行时环境变量中手动设置 `DEEPSEEK_API_KEY`。真实值不进入代码、构建参数、镜像、日志或对话。`.env.example` 仅含占位值；`.env` 由 Git 和 Docker 忽略。

聊天记录写入容器内 `data/messages.json`，首次启动为空；不配置云端持久化，容器被替换或删除后记录可能丢失。Gunicorn 使用单 worker 以配合现有进程内记录状态。

## ACR 构建（待实际完成）

- 个人 Fork：`Craneplayz/isse-labs`。
- 分支：`lab3/2300094603-Xuzhixiang`。
- 构建上下文：`/lab3/2300094603-Xuzhixiang/`。
- Dockerfile：上下文目录内的 `Dockerfile`。
- 地域、镜像仓库、规则标签与构建结果：部署阶段按实际结果补充。

## ECI 与公网验证（待实际完成）

应用实际监听 `5001`；容器启动命令沿用 Dockerfile 的 CMD。实例规格、镜像版本、公网访问地址与验证结果待实际部署后记录。

规定截图将在实际验证后保存为 `screenshots/eci-created.<真实扩展名>` 和 `screenshots/public-page.<真实扩展名>`。真实对话轨迹由学生在实验末尾保存为 `AGENT_TRACE.md`。

## 清理计划

PR 提交后由学生删除本实验 ECI，并检查及释放仅为本实验创建、仍独立存在的 EIP；Agent 核验实际资源状态。建议随后废除实验 Key。

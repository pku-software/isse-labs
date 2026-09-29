# Lab 3：AI 聊天助手云端部署

盛仁杰（2400017748）的 Lab 3 项目，沿用 Lab 2 的 Flask 与原生 HTML/CSS/JavaScript 聊天应用。Flask 提供页面、静态资源及会话和消息 API；前端使用同源相对路径调用 API。后端在运行时从 `DEEPSEEK_API_KEY` 环境变量读取实验 Key。

## 容器构建与运行

ACR 从个人 GitHub Fork 的 `lab3/2400017748-shengrenjie` 分支，以 `/lab3/2400017748-shengrenjie/` 为构建上下文，按本目录的 `Dockerfile` 在云端构建镜像。本地无需 Docker。镜像运行时，Gunicorn 使用单 worker 监听 `0.0.0.0:5001`，由同一 Flask 容器提供页面、静态资源及 API。`EXPOSE 5001` 记录预期端口；公网访问仍取决于 ECI 的网络配置。

`.dockerignore` 排除本地环境变量文件、聊天数据、对话轨迹、截图和缓存。真实 Key 只由本人在 ECI 容器运行时设置为环境变量，不进入源码、GitHub 或镜像。聊天数据写入容器内 `data/`，本实验不提供云端持久化。

## ACR 与 ECI 实验记录

待完成云端构建、ECI 部署及浏览器验证后填写实际地域、仓库、镜像标签、规格、公网访问结果和资源清理记录。

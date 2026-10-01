# Lab 3：将 Flask 聊天应用部署到云端

本项目沿用 Lab 2 的 HTML、CSS、JavaScript 和 Flask 聊天应用。Flask 同时提供静态页面与 JSON API，前端通过同源相对路径访问 API。聊天记录暂存在 Flask 进程内存中，进程重启后会清空。

## 项目文件

- `app.py`：Flask 页面路由、聊天 API 和 DeepSeek 调用。
- `frontend/`：网页、样式和浏览器端 JavaScript。
- `requirements.txt`：Flask、requests 和 Gunicorn 依赖。
- `Dockerfile`：构建 Python 应用镜像，并以 Gunicorn 在容器内监听 `0.0.0.0:5001`。
- `.dockerignore`：避免把本地环境文件、Git 元数据、缓存、轨迹和截图放进镜像构建上下文。

## Key 配置

应用只在服务运行时从 `DEEPSEEK_API_KEY` 环境变量读取 Key。不要把真实 Key 写入源码、`.env.example`、Dockerfile、镜像构建参数或 Git 提交。`.env` 已由 `.gitignore` 和 `.dockerignore` 排除。

## 云端构建与运行

ACR 构建地域、代码分支、构建上下文、Dockerfile 路径和镜像标签：待本次 ACR 构建完成后记录。

ECI 地域、所用镜像版本、实例端口和运行时环境变量名称：待本次 ECI 创建完成后记录。公网访问结果和风险说明：待浏览器验证后补充。

## 实验验证

ACR 构建结果、ECI 实例创建截图和浏览器公网访问截图将在实际操作后补充；此处不预先填写未验证的结果。
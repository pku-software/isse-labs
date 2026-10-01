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

## ACR 云端构建

- ACR 地域：华北 2（北京），私有镜像仓库：`isselab3`。
- 代码源：个人 Fork `joerunrun/isse-labs`。
- 构建分支：`lab3/2300011366-ZhouRungui`。
- 构建上下文：`/lab3/2300011366-ZhouRungui/`；Dockerfile：`Dockerfile`。
- 镜像版本：`lab3-606051b`。ACR 构建成功由学生在控制台确认。
- 代码变更自动构建关闭，海外机器构建开启，缓存保持默认启用；构建由控制台手动触发。

## ECI 运行与公网访问

- 地域：华北 2（北京）；算力类别：经济型；当前实例规格：2 vCPU、4 GiB 内存。
- ECI 使用 ACR 镜像 `isselab3:lab3-606051b`，容器由 Dockerfile 中的 Gunicorn 命令监听 `0.0.0.0:5001`。
- 运行时环境变量名称：`DEEPSEEK_API_KEY`。真实 Key 只在 ECI 容器的运行时配置中设置，不写入源码、镜像或 Git。
- 公网地址：`http://39.106.217.47:5001/`。浏览器截图显示聊天页面已加载。

## 验证记录

- 外部 GET 检查：`/`、`/app.js`、`/style.css`、`/api/hello`、`/api/messages` 均返回 HTTP 200。
- 学生确认已在浏览器测试聊天及记录操作，并使用非敏感内容验证模型回复。
- ECI 运行状态截图：[`screenshots/eci-created.png`](screenshots/eci-created.png)。
- 浏览器公网访问截图：[`screenshots/public-page.png`](screenshots/public-page.png)。

## 公网使用与资源清理

聊天 API 没有身份验证，知道公网地址的人可能调用模型并消耗实验 Key；HTTP 不加密浏览器与服务之间的聊天内容。不要输入敏感信息。提交 PR 后立即删除本次 ECI 实例，并确认与它关联、为本实验创建的 EIP 等计费资源也已释放。实际费用以阿里云控制台和账单为准。

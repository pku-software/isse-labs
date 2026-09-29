# Lab 3 聊天应用

本项目沿用 Lab 2 的 Flask、HTML、CSS 和 JavaScript 聊天应用。页面与 `/api/...` 接口由同一个 Flask 服务提供，前端通过同源相对路径访问接口。应用支持创建、查看、切换、重命名和删除会话，以及发送、修改和删除聊天轮次。

## 配置

后端在运行时读取环境变量 `DEEPSEEK_API_KEY`。`.env.example` 只给出变量名和占位值；不要把真实 Key 写进源码、镜像或 Git。容器中的 Key 由运行平台设置。

会话数据由应用写入 `data/conversations.json`。本实验的云端容器没有持久化存储，容器重建后不能依赖该文件保留记录。

## 容器启动

`Dockerfile` 使用 Python 3.11 安装 `requirements.txt` 中的依赖，复制后端和前端，并以一个 Gunicorn worker 运行 `app:app`，监听 `0.0.0.0:5001`。页面、静态资源与 API 都使用该端口。`.dockerignore` 将本地环境文件、缓存、聊天数据、截图和对话轨迹排除在构建上下文之外。

本实验由 ACR 从个人 GitHub 分支构建镜像，无需在本机安装 Docker。

## ACR 云端构建

- 代码源：个人 GitHub Fork `dhjx1234/isse-labs`。
- ACR 实例地域：华北 2（北京）。
- ACR 镜像命名空间/仓库：`dhjx1234/isse-lab`。
- 构建分支：`lab3/2500013091-yangmuzhi`。
- 构建上下文目录：`/lab3/2500013091-yangmuzhi/`。
- Dockerfile 文件名：`Dockerfile`。
- 构建方式：手动触发；本次构建已由操作者在 ACR 控制台确认成功。

实际镜像标签待从构建规则或 ECI 镜像选择界面确认。ECI 的实际配置与验证结果将在部署阶段补充。

## 非敏感检查接口

`GET /api/hello` 返回中文问候，可用于确认后端已响应。

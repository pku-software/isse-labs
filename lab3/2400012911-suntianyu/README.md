# 知聊：Lab 3 容器部署

本项目从 Lab 2 的 Flask + HTML/CSS/JavaScript 聊天应用迁移而来。Flask 提供页面、静态资源与问答 API；创建问答时，后端读取运行时环境变量 `DEEPSEEK_API_KEY` 并调用 DeepSeek。前端不接收或保存 Key。

## 功能与接口

- `GET /`：聊天页面；`GET /static/...`：前端静态资源。
- `GET /api/hello`：非敏感连通性检查。
- `GET /api/messages`：列出问答。
- `POST /api/messages`：提交 `{ "message": "..." }`，生成并保存一条问答。
- `PATCH /api/messages/<id>`：修改问答中的提问，保留原回复。
- `DELETE /api/messages/<id>`：删除整条问答。

问答写入容器内的 `data/messages.json`。本实验没有配置云端持久化存储；实例重建后记录可能消失，Lab 2 的真实聊天数据不会进入镜像。

## 镜像与运行

ACR 使用本目录作为构建上下文，按 `Dockerfile` 从 `python:3.11-slim` 安装依赖并复制应用。镜像运行时由单个 Gunicorn worker 监听 `0.0.0.0:5001`，入口为 `app:app`。`EXPOSE 5001` 只是镜像端口说明，公网入口还需要 ECI 的网络配置。

真实 Key 仅在 ECI 容器运行时以 `DEEPSEEK_API_KEY` 环境变量设置。`.env`、本地虚拟环境、聊天数据和对话轨迹都被 `.dockerignore` 排除在构建上下文之外；`.env` 也被 Git 忽略。`.env.example` 只有占位值。

## ACR 云端构建

- 地域：华北 2（北京），个人版实例。
- 私有镜像仓库：`binwei114/isse-labs`。
- GitHub 代码源：个人 Fork `binwei114/isse-labs` 的 `lab3/2400012911-suntianyu` 分支。
- 构建上下文：`/lab3/2400012911-suntianyu/`；Dockerfile 文件名：`Dockerfile`。
- 构建规则标签：`lab3-74308eb`；关闭自动构建，手动点击“立即构建”。
- 先开启海外机器构建；学生已在 ACR 构建页确认本次构建成功。

本地代码更新后，要先 Commit 并 Push 到上述 GitHub 分支，再手动触发 ACR 新构建。只有本 README 等文档变化时，无需为旧代码重新构建镜像。

ECI 配置与公网验证结果将在对应实验步骤完成后补充。

# Lab 3：ACR 构建与 ECI 部署

姓名：王珮源；学号：2500013167。

## 项目来源与架构

沿用 Lab 2 的 Flask + HTML/CSS/JavaScript 聊天应用。同一 Flask 应用提供首页、静态资源与 `/api/messages` 的创建、查看、修改、删除接口，`/api/hello` 用于连通性检查。前端使用同源相对路径，输入、编辑与删除确认在页面内完成。

创建记录时后端调用 DeepSeek；修改只修改用户消息，不重新生成回复。聊天记录保存在进程内存，重启后清空，本实验不配置持久化。模型沿用 Lab 2 的 `deepseek-flash`，实际模型调用尚待云端验证。

Key 仅由后端在运行时读取 `DEEPSEEK_API_KEY` 环境变量。ECI 部署时由学生手动设置，不写入源码、镜像或构建参数。`.env.example` 仅说明变量名和占位值；应用不会自动加载 `.env`。

## Dockerfile

使用 `python:3.12-slim`，工作目录 `/app`。先复制依赖清单并安装 Flask、requests、Gunicorn，再复制后端与前端，便于构建器在依赖未变化时复用安装层。

运行命令为 `gunicorn --workers 1 --bind 0.0.0.0:5001 --timeout 90 app:app`。单 worker 保持内存聊天记录一致；90 秒 worker 超时高于模型请求的 60 秒超时。`app:app` 指 `app.py` 中的 Flask 对象 `app`。云端不使用 Flask debug 服务器。

`EXPOSE 5001` 声明预期端口，不能自动创建公网入口或放行网络。`.dockerignore` 只允许应用、依赖清单与前端进入构建上下文，排除环境文件、虚拟环境、缓存、截图、README 和对话轨迹。

## ACR 构建配置

- 代码源：个人 Fork `CountlessBugs/isse-labs`。
- 分支：`lab3/2500013167-WangPeiyuan`。
- 构建上下文：`/lab3/2500013167-WangPeiyuan/`。
- Dockerfile：上下文中的 `Dockerfile`。
- 实际地域：华北 2（北京）。
- ACR 命名空间：countlessbugs-lab3；私有仓库：lab3-wangpeiyuan。
- 镜像标签：lab3-5ce69cf；对应应用提交：5ce69cf。
- 构建方式：海外机器构建，关闭代码变更自动构建，手动触发。
- 构建结果：学生已在 ACR 构建页确认成功；具体镜像地址待 ECI 选择时记录。
- 更新流程：本地修改、Commit、Push 到个人分支，再手动触发 ACR 构建。

## ECI 配置与访问验证

尚未创建实例。实例规格、镜像地址、实际地域、运行时环境变量名称、公网访问与两张截图待实际操作后补充，不将本地测试视为云端验证。

## 提交与清理计划

完成构建和浏览器验证后提交个人 README、两张原始截图和真实 Codex 对话轨迹，发起中文 PR。PR 提交后立即删除实验 ECI，并核对关联 EIP 是否仍独立计费。

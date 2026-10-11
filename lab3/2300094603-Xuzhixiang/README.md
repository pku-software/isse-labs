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

## ACR 构建

- 个人 Fork：`Craneplayz/isse-labs`。
- 分支：`lab3/2300094603-Xuzhixiang`。
- 构建上下文：`/lab3/2300094603-Xuzhixiang/`。
- Dockerfile：上下文目录内的 `Dockerfile`。
- 地域：华北 2（北京，`cn-beijing`）。
- 私有镜像仓库：`craneplayz-lab/lab3-chat`。
- 镜像标签：`lab3-0c79d65`，对应代码提交 `0c79d65`。
- 开启海外机器构建，关闭自动构建，手动立即构建；学生报告构建页显示成功。
- 完整镜像地址待 ECI 选择时补充。本地修改后需先 Commit、Push，再由 ACR 重新构建；ECI 使用新镜像运行容器。

## ECI 与公网验证

- 地域：华北 2（北京），可用区 H；实例名称 `lab3-2300094603`。
- 经济型，0.25 vCPU、0.5 GiB（控制台显示 512 MiB），按量付费。
- 镜像：`crpi-ev2srl9z7y245d36-vpc.cn-beijing.personal.cr.aliyuncs.com/craneplayz-lab/lab3-chat:lab3-0c79d65`。
- 应用监听 `0.0.0.0:5001`；容器启动命令沿用 Dockerfile 的 CMD，运行日志显示 Gunicorn 与 worker 已启动。
- 运行时环境变量名称：`DEEPSEEK_API_KEY`，真实值由学生自行配置。
- 本次演示地址：`http://47.95.204.198:5001/`。这是临时实验入口，清理后不保证可用。
- 初次公网访问失败，检查运行日志后由学生调整绑定安全组；随后 Agent 核验首页、JS、CSS、`/api/hello` 和 `/api/messages` 均返回 HTTP 200。
- 学生浏览器截图确认页面加载和一次非敏感模型回复；学生报告刷新后记录保留、修改、删除均测试成功。Agent 未代学生执行浏览器操作。

浏览器请求经公网 EIP 和网络规则到达容器 5001 端口，由 Gunicorn 接收并交给 Flask 处理。其他设备可通过同一公网入口访问。

该演示使用 HTTP，聊天内容未加密；API 无鉴权，其他人可能读取、修改或删除聊天记录，以及调用模型消耗实验额度。Key 保留在后端，不随前端请求传输。

规定原始截图：

- [ECI 已创建并运行](screenshots/eci-created.png)
- [学生浏览器公网访问与模型回复](screenshots/public-page.png)

真实对话轨迹由学生在实验末尾保存为 `AGENT_TRACE.md`。

## 清理计划

PR 提交后由学生删除本实验 ECI，并检查及释放仅为本实验创建、仍独立存在的 EIP；Agent 核验实际资源状态。建议随后废除实验 Key。

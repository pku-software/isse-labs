# Lab 3：AI 聊天应用的容器化与云端部署

陈楷舜 · 2500018733

基于本人 Lab 2 的 HTML/CSS/JavaScript + Flask + DeepSeek 应用，保留会话管理、独立多轮上下文和问答记录的增删改查，增加用于 ACR 云端构建和 ECI 运行的容器配置。

课程基线：`pku-software/isse-labs` 提交 `61b99f94587cc784191cb90df3ab63b2b2abef5a`。个人分支为 `lab3/2500018733-ChenKaishun`。

## 运行架构

GitHub 个人分支保存源码与 Dockerfile；ACR 从该分支构建并保存镜像；ECI 拉取镜像并启动容器。容器内的 Gunicorn 加载 `app.py` 中的 Flask 对象 `app`，在同一端口提供网页、静态资源和 JSON API。

浏览器使用 `/api/...` 相对路径调用 Flask；Flask 在运行时读取 `DEEPSEEK_API_KEY` 环境变量，并调用 DeepSeek。前端不读取或接收 Key。

## Dockerfile

- 基础镜像：`python:3.13-slim`；容器工作目录：`/app`。
- 先复制 `requirements.txt` 并安装依赖，再复制 `app.py` 和 `frontend/`。只修改源码时，依赖安装步骤可能复用构建缓存。
- `PYTHONDONTWRITEBYTECODE=1` 禁止生成 Python 字节码缓存；`PYTHONUNBUFFERED=1` 让运行日志及时输出。两者均为非敏感运行设置。
- `EXPOSE 5001` 描述服务端口，不会自动创建公网入口或放行网络规则。
- 启动命令：`gunicorn --bind 0.0.0.0:5001 --workers 1 --threads 4 --timeout 90 app:app`。
- 使用单 worker，避免多个进程分别维护会话内存并竞争写入同一个 JSON 文件；4 个线程可在等待模型时继续响应其他请求，应用现有的锁保护共享数据。
- `--timeout 90` 是 Gunicorn worker 无响应超时设置；线程 worker 下不应把它理解为每个 HTTP 请求的严格期限。DeepSeek 调用本身保留连接 10 秒、读取 60 秒的超时配置。
- 容器使用 Gunicorn，不使用 Flask debug 服务器。修改源码或依赖后，必须重新构建镜像并让 ECI 运行新版本。

构建按指令顺序进行，某一步失败或中断后，后续步骤不会继续。修复后应重新触发构建；未变化的前序步骤可能命中缓存，ACR 不保证从中断处接着执行。

`.dockerignore` 默认排除全部内容，仅放行五个应用文件和前端目录。真实 `.env`、虚拟环境、聊天数据、截图、对话轨迹及 Git 文件不进入构建上下文。Dockerfile 和 `.dockerignore` 由构建工具作为构建配置读取，不复制到应用镜像。

## 环境与数据

`.env.example` 只有占位值。本地可自行配置 `.env`；ECI 中由本人在容器运行时环境变量中设置真实 Key。不要将 Key 放进 Dockerfile、构建参数、代码或文档。进程环境变量优先于本地 `.env`。

未设置 Key 时，网页、健康接口及会话 CRUD 仍可运行；请求模型返回清晰的 `503` 错误。

保留 Lab 2 的 JSON 存储逻辑，启动时在容器内创建 `data/conversations.json`。没有迁移 Lab 2 的聊天数据。本实验不配置云端持久化，容器重建、替换或释放后，不保证聊天记录保留。`data/` 同时被 Git 和镜像构建排除。

## 本地检查（Windows PowerShell）

在本 README 所在目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

本机访问 `http://localhost:5001/`。直接运行 `app.py` 仅监听本机且关闭 debug；Gunicorn 在 ACR 构建的 Linux 镜像中运行，无需在 Windows 上启动 Gunicorn，也无需安装本地 Docker。

在第二个 PowerShell 窗口可检查非模型接口：

```powershell
Invoke-RestMethod http://localhost:5001/api/hello
Invoke-RestMethod http://localhost:5001/api/conversations
```

## 主要 API

- `GET /`、`GET /style.css`、`GET /app.js`：网页和静态资源。
- `GET /api/hello`：非敏感健康检查，返回 `{"message":"你好"}`。
- `GET /api/conversations`、`POST /api/conversations`：列出或新建会话；新建正文为 `{"title":"会话名称"}`。
- `GET/PATCH/DELETE /api/conversations/<id>`：读取、重命名或删除会话。
- `GET/POST /api/conversations/<id>/messages`：读取或创建问答；提问正文为 `{"message":"问题"}`。
- `PATCH/DELETE /api/conversations/<id>/messages/<message_id>`：修改问题或删除问答；修改不会重新生成已有回答。
- 保留 Lab 2 的 `/api/messages` 兼容接口。

模型只接收当前会话最近 10 轮问答和本次问题。删除成功返回 `204`；输入错误返回 `400/415`，记录不存在返回 `404`，生成期间历史发生变更返回 `409`，上游异常、配置错误或超时返回 `502/503/504`。

## 部署记录

本地验证已通过：28 项应用检查覆盖页面及静态资源、健康接口、会话和问答 CRUD、多轮上下文隔离、JSON 重新加载、错误输入和缺少 Key 的处理；JavaScript 语法检查通过。模型响应为测试替身，测试禁用 `.env` 加载及真实网络请求，因此不代表真实模型或云端容器已经验证。已确认 `.env`、数据和本地验证文件被 Git 忽略，且课程说明与 Lab 2 原目录未改动。

当前尚未进行 ACR 构建与 ECI 部署。以下为已确定的构建输入，实际镜像地址、版本和云端验证结果在完成相应操作后补充。

- 个人 GitHub 仓库：`Mike32chen/isse-labs`。
- 构建分支：`lab3/2500018733-ChenKaishun`。
- 构建上下文：`/lab3/2500018733-ChenKaishun/`。
- Dockerfile：上下文根目录内的 `Dockerfile`，按 ACR 页面字段定义填写路径。
- 计划地域：华北 2（北京），ACR 与 ECI 同地域。
- 运行端口：`5001/TCP`；运行时环境变量名称：`DEEPSEEK_API_KEY`。
- 镜像标签、ACR 地址、ECI 实例与规格、公网地址：尚未产生。
- ACR 构建、公网访问、真实模型调用：尚未验证。
- 规定的实例创建截图、本人浏览器公网访问截图、真实对话轨迹：待对应步骤完成后添加。
- 本实验尚未创建云资源。

## 参考

- [课程 Lab 3 说明](https://github.com/pku-software/isse-labs/blob/61b99f94587cc784191cb90df3ab63b2b2abef5a/lab3/README.md)
- [Docker 构建最佳实践](https://docs.docker.com/build/building/best-practices/)
- [Gunicorn 参数说明](https://gunicorn.org/reference/settings/)

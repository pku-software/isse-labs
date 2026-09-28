# Lab 3 云端聊天应用

本项目沿用 Lab 2 的 HTML、CSS、JavaScript 与 Flask 聊天应用，由同一个 Flask/Gunicorn 服务提供网页、静态资源和 API。前端通过同源相对路径请求 API；后端仅在运行时从 `DEEPSEEK_API_KEY` 环境变量读取 DeepSeek Key。

## 本地运行

1. 安装 Python 3.12 或兼容版本。
2. 安装依赖：`python -m pip install -r requirements.txt`。
3. 在本机自行创建 `.env`，设置 `DEEPSEEK_API_KEY`。不要提交真实 Key。
4. 开发时运行 `python app.py`，访问 `http://localhost:5001/`。

## 容器构建与运行

Dockerfile 使用 Python 3.12 slim 基础镜像，在 `/app` 安装 `requirements.txt` 中的依赖，再复制 Flask 应用和前端文件。容器通过 Gunicorn 单 worker 监听 `0.0.0.0:5001`。`EXPOSE 5001` 只声明容器预期端口，不会自行创建公网入口。

本 Lab 不要求在本机安装 Docker。本次使用华北 2（北京）的 ACR 个人版实例，命名空间为 `lab3`，私有镜像仓库为 `chat-app`。代码源是个人 GitHub Fork `Zheng-Matt/isse-labs`；构建分支为 `lab3/2500017738-ZhengZixuan`，构建上下文为 `/lab3/2500017738-ZhengZixuan/`，Dockerfile 文件名为 `Dockerfile`，镜像标签为 `lab3-3919686`。本次构建由学生在控制台确认成功；自动构建关闭，海外机器构建开启。后续代码更新需先推送到该 GitHub 分支，再在 ACR 手动触发构建。

## ECI 运行配置

在与 ACR 镜像相同地域创建 ECI，选择本次 ACR 构建的镜像和标签。保持镜像默认启动命令，使其执行 Dockerfile 中的 Gunicorn `CMD`。在容器运行时环境变量中由操作者设置 `DEEPSEEK_API_KEY`；不要把 Key 写入源码、镜像或构建参数。

ECI 网络入口及实际费用以创建时控制台显示为准。应用监听端口为 `5001`。完成部署后记录实际地域、镜像标签、规格和公网访问地址（不要记录 Key）。

## API 与验证

- `GET /api/hello`：服务问候检查。
- `/api/conversations` 及其子路由：多会话的创建、读取、重命名、删除和消息发送。
- `/api/messages` 及其子路由：兼容的聊天记录 CRUD 接口。

部署验证时，在浏览器访问 `http://<ECI公网IP>:5001/`，检查页面和静态资源，并以非敏感内容验证会话操作及模型回复。公网验证完成后按课程要求提交 ECI 创建截图和浏览器地址栏截图，并清理实验计费资源。

## 数据与安全

Lab 2 的 JSON 文件持久化代码会保留，但本 Lab 的 ECI 不配置持久化存储，容器重建后数据可能丢失。`.dockerignore` 排除环境变量文件、虚拟环境、缓存、Git 元数据、数据目录和对话轨迹。`.env.example` 仅提供变量名及占位值。

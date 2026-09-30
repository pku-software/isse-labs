# Lab 3：AI 聊天应用的容器化与云端部署

本项目在 Lab 2 的 AI 聊天 Web 应用基础上，练习把已有应用打包成容器镜像并放到云端运行：
前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask，通过 DeepSeek 官方 API 获取模型回复。
本次不新增聊天功能，重点是 **Dockerfile → 镜像 → 容器** 这条链路，以及 **ACR 云端构建 → ECI 运行** 的部署方式。

## 项目来源与架构

- 应用代码来自 Lab 2 的个人成果（`lab2/蒋徐祺-2400017727/`），前端页面、静态资源和 CRUD API 保持原样。
- 运行链路：浏览器 → 公网 IP:5001 → ECI 中的容器 → Gunicorn → Flask（提供页面、静态资源和 API）。
- 同一个容器同时提供页面、静态资源和 API，前端 `fetch()` 使用同源相对路径 `/api/messages`。
- 聊天记录仍保存在 Flask 进程的内存中，容器重启后会清空；本 Lab 不要求云端持久化。
- DeepSeek API Key 只由后端在运行时从环境变量 `DEEPSEEK_API_KEY` 读取，前端不接触 Key。

## 目录结构

```text
.
├── app.py              # Flask 后端：提供前端页面与聊天 API
├── frontend/
│   ├── index.html      # 页面结构
│   ├── style.css       # 页面样式
│   └── app.js          # 页面逻辑，通过 fetch() 调用后端 API
├── requirements.txt    # 后端依赖（含 Gunicorn）
├── Dockerfile          # 构建镜像的说明
├── .dockerignore       # 构建上下文排除清单
├── .gitignore          # 忽略 .env、缓存、虚拟环境等
├── .env.example        # 环境变量示例（不含真实 Key）
├── screenshots/        # 必交截图：ECI 已创建、浏览器公网访问
└── AGENT_TRACE.md      # 由学生保存的真实 Codex 对话轨迹
```

## 环境变量

后端只读取一个变量：

```text
DEEPSEEK_API_KEY=your_api_key_here
```

- 本地运行：复制 `.env.example` 为 `.env`，把值换成自己的实验 Key（`.env` 已被 `.gitignore` 忽略）。
- 云端运行：在 ECI 的容器配置里以**环境变量**方式设置同名变量，Key 不进入源码、镜像或构建参数。

## 本地运行（可选）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

浏览器打开 `http://localhost:5001/`。本 Lab 不要求在本机安装 Docker，镜像由 ACR 在云端构建。

## Dockerfile 关键配置

| 指令 | 作用 |
| --- | --- |
| `FROM python:3.12-slim` | 选择自带 Python 与 pip 的基础镜像，体积较小且不含实验 Key |
| `WORKDIR /app` | 设定容器内工作目录，后续相对路径都以它为基准 |
| `COPY requirements.txt ./` + `RUN pip install --no-cache-dir -r requirements.txt` | 先复制依赖清单并安装，源码变动时这一层仍可复用缓存 |
| `COPY app.py ./`、`COPY frontend ./frontend` | 构建阶段复制应用与前端文件，`.dockerignore` 已排除密钥与无用文件 |
| `EXPOSE 5001` | 声明容器预期提供的端口，只是元数据，不会自动开放公网 |
| `CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5001", "app:app"]` | 运行阶段以 Gunicorn 单 worker 监听 `0.0.0.0:5001`，替代 Flask debug 服务器 |

`.dockerignore` 排除了 `.env`、`.venv/`、`__pycache__/`、`.git/`、`README.md`、`AGENT_TRACE.md`、`screenshots/`，
这些内容留在仓库里即可，运行镜像并不需要。

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 返回前端页面 `index.html` |
| GET | `/api/hello` | 连通性测试，返回 `{"message": "你好"}` |
| GET | `/api/messages` | 返回全部聊天记录 |
| POST | `/api/messages` | 创建一条记录，请求体 `{"message": "..."}`，`reply` 由 DeepSeek 生成 |
| PATCH | `/api/messages/<id>` | 修改指定记录的 `message` |
| DELETE | `/api/messages/<id>` | 删除指定记录 |

## 阿里云 ACR 云端构建记录

> 任务 2 完成后在此补充：ACR 地域、命名空间与仓库、构建分支、构建上下文目录、镜像版本标签。

## 阿里云 ECI 部署记录

> 任务 3、4 完成后在此补充：ECI 地域与规格、镜像与标签、环境变量名称、公网访问方式与验证结论。

## 资源清理

本实验为短时演示，验证完成后必须删除 ECI 实例，并检查随实例自动创建的弹性公网 IP 是否仍需独立释放。

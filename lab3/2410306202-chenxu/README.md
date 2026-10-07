# Lab 3：从代码到云端 —— ACR 构建与 ECI 部署

本目录是 Lab 3 的个人实验目录（陈旭，学号 2410306202）。

## 一、项目来源与架构

- 课程仓库：ISSE Labs 2026（Fork 自课程官方仓库 `pku-software/isse-labs`）
- 个人 Fork：<https://github.com/LinyuanChen05/isse-labs>
- 本次分支：`lab3/2410306202-chenxu`
- 应用来源：Lab 2 的 `lab2/陈旭-2410306202/`，这里只保留运行所需的非敏感文件

应用仍然是一个 Flask 聊天程序，一个进程同时承担两件事：

1. 提供前端页面与静态资源：`/`、`/style.css`、`/app.js`；
2. 提供聊天 API：会话接口 `/api/conversations...`，另有兼容接口 `/api/messages...`。

前端使用**同源相对路径**的 `fetch()`，不写死后端地址，因此部署到云端后前端无需修改。

**API Key 只由后端持有**：服务端在运行时从环境变量 `DEEPSEEK_API_KEY` 读取 Key，用于调用 DeepSeek。
前端不输入、不接收、不保存 Key。真实 Key 不进入源码、Dockerfile、构建上下文、镜像、日志或对话。

## 二、目录结构

```
lab3/2410306202-chenxu/
├── app.py              # Flask 后端：页面/静态资源 + 聊天 API
├── frontend/           # 前端：index.html、style.css、app.js
├── requirements.txt    # Python 依赖（含 gunicorn）
├── Dockerfile          # 镜像构建说明
├── .dockerignore       # 构建上下文排除项
├── .gitignore          # 忽略 .env、虚拟环境、运行时数据等
├── .env.example        # 只有变量名与占位值
├── README.md
├── screenshots/        # 必交截图（ECI 创建成功、浏览器公网访问）
└── AGENT_TRACE.md      # 真实 Codex 对话轨迹（由学生本人保存）
```

## 三、Dockerfile 关键配置

| 指令 | 作用 |
| --- | --- |
| `FROM python:3.12-slim` | 选择含 Python 的精简基础镜像 |
| `WORKDIR /app` | 设置容器内工作目录 |
| `COPY requirements.txt ./` | 先只复制依赖清单，便于利用构建缓存 |
| `RUN pip install --no-cache-dir -r requirements.txt` | 构建阶段安装依赖（含 gunicorn） |
| `COPY . .` | 复制应用与前端（`.dockerignore` 已排除敏感/无关文件） |
| `EXPOSE 5001` | 声明容器预期提供的端口（元数据，不会自动开放公网） |
| `CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5001", "app:app"]` | 运行阶段以单 worker 的 Gunicorn 启动 Flask 应用，监听 0.0.0.0:5001 |

`.dockerignore` 排除 `.env`、`.git`、`data/`、虚拟环境、`AGENT_TRACE.md`、`screenshots/` 等，
确保真实 Key 与聊天数据不会进入构建上下文和镜像。

## 四、镜像构建（ACR）

> 本阶段信息在完成任务 2 后补充。

## 五、云端运行（ECI）

> 本阶段信息在完成任务 3 后补充。

## 六、公网访问与安全说明

> 本阶段信息在完成任务 4 后补充。
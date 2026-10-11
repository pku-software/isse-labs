# Lab 3：AI 聊天应用的容器化与云端部署

本项目由 Lab 2 的 HTML / CSS / JavaScript + Flask + DeepSeek 聊天应用延续而来。Lab 3 不再增加聊天功能，而是把已有应用打包成容器镜像，并放到云端的弹性容器实例（ECI）上运行，让浏览器可以通过公网访问。

## 项目功能

- 浏览器打开聊天页面，输入消息后发送给后端；
- 后端调用 DeepSeek API 生成真实回复；
- 以“一次问答”为一条聊天记录，支持创建、读取、修改、删除；
- API Key 只保存在后端运行时环境变量中，前端不接触、不保存 Key。

## 目录结构

```text
2400018614-xiaoshadi/
├── app.py              # Flask 后端：同时提供前端页面和聊天 API
├── frontend/           # 前端页面与静态资源
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt    # Python 依赖（含 gunicorn）
├── Dockerfile          # 镜像构建说明
├── .dockerignore       # 构建上下文排除项
├── .gitignore          # Git 忽略项（.env、缓存、虚拟环境）
├── .env.example        # 环境变量示例，只有占位值
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 API Key

把 `.env.example` 复制为 `.env`，填入自己的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 已被 `.gitignore` 忽略，不会被提交；真实 Key 不要写入代码或提交到仓库。

## 启动应用

开发时可以直接用 Flask：

```bash
python app.py
```

在容器或正式运行场景中，用 Gunicorn 启动：

```bash
gunicorn --bind 0.0.0.0:5001 --workers 1 --timeout 90 app:app
```

启动后浏览器访问 http://localhost:5001/ 。

## API 清单

| 方法   | 路径                 | 作用                    |
| ------ | -------------------- | ----------------------- |
| GET    | `/api/hello`         | 连通性检查              |
| GET    | `/api/messages`      | 读取全部聊天记录        |
| POST   | `/api/messages`      | 创建记录并调用 DeepSeek |
| PATCH  | `/api/messages/<id>` | 修改指定记录的 message  |
| DELETE | `/api/messages/<id>` | 删除指定记录            |

最简单的接口测试：

```bash
curl http://localhost:5001/api/hello
```

## 容器化

`Dockerfile` 说明镜像如何构建：选择 Python 基础镜像、先安装依赖、再复制应用与前端，最后由 Gunicorn 监听 `0.0.0.0:5001` 启动 Flask 应用。本实验不要求在本机安装 Docker，只用它在云端（ACR）构建。

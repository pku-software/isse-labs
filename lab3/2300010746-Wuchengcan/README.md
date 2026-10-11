# AI 聊天 Web 应用

在浏览器中使用的聊天应用。前端页面通过 Flask API 收发消息，后端调用 DeepSeek 生成回复。本地运行时，API Key 放在后端的 `.env` 中。云端运行时，由 ECI 的环境变量 `DEEPSEEK_API_KEY` 提供，不写入镜像或仓库。

一条聊天记录的形状为：

```json
{"id": 1, "message": "用户输入", "reply": "模型回复"}
```

记录保存在当前 Python 进程的内存中。Flask 重启后，这些记录会清空。

## 项目功能

- 浏览器中发送消息，并显示用户内容和模型回复
- 打开页面时加载当前进程中的全部记录
- 修改或删除一条记录，操作后页面立即更新
- `GET /api/hello` 用于检查服务是否可用

## 安装依赖

在个人项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 配置

复制示例文件并填写自己的 Key：

```powershell
copy .env.example .env
```

`.env` 中只保留一行，把占位符换成真实 Key：

```text
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 已被 `.gitignore` 忽略，不要把真实 Key 写入代码或提交到 Git。

## 启动

```powershell
.\.venv\Scripts\python.exe app.py
```

Flask 监听 `5001` 端口。保持这个终端运行。

## 访问地址

http://localhost:5001/

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 返回前端页面 |
| GET | `/api/hello` | 返回 `{"message":"你好"}` |
| GET | `/api/messages` | 返回全部聊天记录 |
| POST | `/api/messages` | 创建记录。请求体为 `{"message":"用户输入"}`，`reply` 为 DeepSeek 返回的文本 |
| PATCH | `/api/messages/<id>` | 修改指定记录的 `message` |
| DELETE | `/api/messages/<id>` | 删除指定记录 |

缺少 `message`、内容为空或 `id` 不存在时，接口返回 JSON 错误和对应的 HTTP 状态码。Key 缺失或模型调用失败时同样返回 JSON 错误。

## API 测试

服务启动后，在另一个终端执行。

检查服务：

```powershell
curl.exe http://localhost:5001/api/hello
```

发送一条消息：

```powershell
curl.exe -X POST http://localhost:5001/api/messages -H "Content-Type: application/json" -d '{"message":"请用一句话介绍北京大学"}'
```

返回中应包含 `id`、`message` 和模型生成的 `reply`，且不包含 API Key。

## 选做功能

未实现 JSON 文件持久化，也未实现多个聊天会话。

## ACR 构建

镜像由阿里云容器镜像服务在云端构建，不在本机构建。

| 项目 | 值 |
| --- | --- |
| 地域 | 华北 2（北京） |
| 命名空间 | `wuchengcan` |
| 镜像仓库 | `lab3-chat`（私有） |
| 代码来源 | GitHub `ChengcanWu/isse-labs` |
| 分支 | `lab3/2300010746-Wuchengcan` |
| 构建上下文 | `/lab3/2300010746-Wuchengcan/` |
| Dockerfile | `Dockerfile` |
| 镜像标签 | `lab3-8b682c1` |
| 镜像地址 | `crpi-fom4qze0yaawfevk.cn-beijing.personal.cr.aliyuncs.com/wuchengcan/lab3-chat:lab3-8b682c1` |

## 部署方式

GitHub 分支 `lab3/2300010746-Wuchengcan` 存放源码和 Dockerfile。ACR 在北京云端构建镜像。ECI 拉取标签 `lab3-8b682c1` 并运行容器。容器内 Gunicorn 使用 1 个 worker，监听 `0.0.0.0:5001`，入口是 `app:app`。同一个进程提供页面、静态文件和 API。聊天记录只保存在该进程的内存中，实例重启后会清空。

Dockerfile 使用基础镜像 `docker.m.daocloud.io/library/python:3.12-slim`。构建时先复制并安装 `requirements.txt`，再复制 `app.py` 和 `frontend/`。`EXPOSE 5001` 只声明端口，公网入口来自 ECI 的弹性公网 IP，以及安全组对 TCP `5001` 的入方向放行。

## ECI

| 项目 | 值 |
| --- | --- |
| 实例名称 | `lab3-2300010746` |
| 实例 ID | `eci-2zeenwsi6qz0ux0htsph` |
| 地域 | 华北 2（北京），可用区 H |
| 规格 | 按量付费，经济型，0.25 vCPU，512 MiB |
| 弹性公网 IP | `47.94.16.145` |
| 应用端口 | `5001` |
| 环境变量名称 | `DEEPSEEK_API_KEY` |
| 安全组 | `sg-2zeee69ujx82e95x4dh3`，入方向允许 TCP `5001`，来源 `0.0.0.0/0` |

## 公网验证

浏览器访问 http://47.94.16.145:5001/ 。页面显示「AI 聊天」，样式和脚本已加载。`GET /api/hello` 返回 `{"message":"你好"}`。发送「你好」后，页面出现模型回复，`GET /api/messages` 能读到这条记录，响应中没有 API Key。

## 风险与清理

这个地址对公网开放，接口没有登录验证。其他人可以查看、发送、修改和删除消息；发送消息会调用 DeepSeek 并消耗额度。访问使用 HTTP，聊天内容在传输中不加密。

提交 PR 后删除实例 `eci-2zeenwsi6qz0ux0htsph`（名称 `lab3-2300010746`），并确认弹性公网 IP `47.94.16.145` 不再单独计费。截图保留。实验使用的 DeepSeek Key 建议在删除实例后废除。

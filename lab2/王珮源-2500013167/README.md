# AI 聊天 Web 应用

一个最小但完整的网页聊天应用：前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask
并监听 `5001` 端口；前端通过 `fetch()` 调用自己的 Flask API，Flask 再调用 DeepSeek API
生成回复。聊天记录以「一次问答」为一条记录，支持创建、查看、修改和删除。

## 功能

- 在浏览器里与 DeepSeek 模型对话，每次发送产生一条记录，包含用户消息和模型回复；
- 页面打开时自动加载已有记录，每条记录下方提供「修改」「删除」入口；
- 输入、确认与错误提示全部显示在页面内，不使用浏览器弹窗；
- 聊天记录保存在 Flask 进程的内存里，重启后端后会清空（未做持久化）。

## 目录结构

- `app.py`：Flask 后端入口，同时提供前端页面与 API
- `frontend/index.html`、`frontend/style.css`、`frontend/app.js`：前端页面、样式与脚本
- `.env.example`：环境变量示例文件（只包含占位符）
- `.env`：本地真实 API Key 文件，已被 `.gitignore` 忽略，不进入版本库
- `requirements.txt`：Python 依赖列表

## 安装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env`，把占位符换成自己的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 只存在于本地，不会进入版本库。后端启动时会读取它，把 Key 放进进程的环境变量；
浏览器端始终拿不到这个 Key。如果没有配置，创建记录的接口会返回 500 和一句说明。

## 启动

在项目目录下执行：

```bash
python app.py
```

Flask 以开发模式启动并监听 `5001` 端口（开启调试，改动代码后自动重启）。

## 浏览器访问

打开 `http://localhost:5001/` 即可使用聊天页面；页面和 API 由同一个 Flask 进程提供。

## API 说明

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/hello` | 连通性检查，返回 `{"message":"你好"}` |
| POST | `/api/messages` | 新建记录，请求体 `{"message":"..."}`，返回 201 与 `{"id":1,"message":"...","reply":"..."}` |
| GET | `/api/messages` | 返回全部聊天记录 |
| PATCH | `/api/messages/<id>` | 修改记录的 `message`，请求体同上，返回修改后的记录 |
| DELETE | `/api/messages/<id>` | 删除指定记录，返回 `{"id":1,"deleted":true}` |

出错时统一返回 `{"error":"..."}`：请求体缺少 `message` 是 400，id 不存在是 404，
服务端没读到 API Key 是 500，调用 DeepSeek 失败是 502。

## 最简单的 API 测试

```bash
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

在 Windows PowerShell 里，参数中的双引号需要转义：

```powershell
curl.exe -X POST "http://localhost:5001/api/messages" `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"请用一句话介绍北京大学\"}'
```

## 选做功能

未完成选做任务：没有实现 JSON 文件持久化，也没有实现多会话与多轮对话。

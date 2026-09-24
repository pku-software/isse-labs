# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：在浏览器里向 AI 提问、查看回复，并对每条聊天记录做修改和删除。

前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask。前端只调用自己后端的 RESTful API，真正的模型调用发生在 Flask 后端；API Key 只保存在后端，通过 `.env` 管理，不会出现在页面、JavaScript 或 Git 中。

## 功能

- 在页面中输入消息并发送，由后端调用 DeepSeek API 返回真实回复
- 页面展示已有的聊天记录，每条包含用户消息和 AI 回复
- 每条记录可以修改消息内容，也可以删除
- 修改、删除的确认过程以及加载状态和错误提示都显示在页面内，不使用浏览器弹窗

## 项目结构

```text
.
├── app.py              Flask 后端：提供前端页面、静态资源和聊天记录 API
├── frontend/
│   ├── index.html      页面结构
│   ├── style.css       页面样式
│   └── app.js          前端逻辑，通过 fetch 调用后端 API
├── .env.example        环境变量示例文件
├── .gitignore          忽略 .env、__pycache__/、.venv/
├── requirements.txt    Python 依赖
└── README.md
```

## 环境要求

- Python 3（建议 3.10 或更高版本）

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

会安装 Flask、python-dotenv 和 requests。

## 配置 API Key

1. 从示例文件复制出一份本地配置：

```powershell
Copy-Item .env.example .env
```

```bash
cp .env.example .env
```

2. 打开 `.env`，把示例值替换成你自己的 DeepSeek API Key，等号两边不要加空格，也不要加引号：

```text
DEEPSEEK_API_KEY=你的真实APIKey
```

3. DeepSeek API Key 可以在 <https://platform.deepseek.com/api_keys> 创建，接口文档见 <https://api-docs.deepseek.com/zh-cn/>。

`.env` 已经被 `.gitignore` 忽略，不会被提交；请不要把它或真实 Key 写进任何会被提交的文件。

## 启动

在项目根目录执行：

```bash
python app.py
```

Flask 监听 `5001` 端口，日志中出现 `Running on http://127.0.0.1:5001` 即表示启动成功，按 `Ctrl+C` 停止服务。

浏览器访问地址：

```text
http://localhost:5001/
```

这个地址同时提供前端页面和 API，不需要再单独启动前端服务。

## 数据存储

聊天记录保存在 Flask 进程的内存中，既不使用数据库，也不写入文件。停止或重启 Flask 后，已有记录会全部消失。

## API

一条聊天记录的数据结构：

```json
{"id": 1, "message": "用户输入", "reply": "后端回复"}
```

| 方法 | 路径 | 说明 | 成功状态码 |
| --- | --- | --- | --- |
| GET | `/api/hello` | 连通性检查，返回 `{"message": "你好"}` | 200 |
| GET | `/api/messages` | 读取全部聊天记录 | 200 |
| POST | `/api/messages` | 创建一条记录，调用模型生成 `reply` | 201 |
| PATCH | `/api/messages/<id>` | 修改指定记录的 `message` | 200 |
| DELETE | `/api/messages/<id>` | 删除指定记录 | 200 |

请求体统一使用 JSON，并带上 `Content-Type: application/json`。出错时返回 JSON 格式的错误说明：

| 状态码 | 场景 |
| --- | --- |
| 400 | 请求体不是 JSON 对象，或 `message` 字段缺失、内容为空 |
| 404 | `PATCH` / `DELETE` 指定的 `id` 不存在 |
| 502 | 后端没有读到 API Key，或调用 DeepSeek 请求失败 |

## API 测试

先启动 Flask，再另开一个终端执行下面的命令。

检查服务是否存活：

```bash
curl http://localhost:5001/api/hello
```

创建一条聊天记录，`reply` 由 DeepSeek 生成：

```bash
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

读取全部记录：

```bash
curl http://localhost:5001/api/messages
```

修改某条记录的 `message`，把 `1` 换成实际存在的 id：

```bash
curl -X PATCH http://localhost:5001/api/messages/1 \
  -H "Content-Type: application/json" \
  -d '{"message":"修改后的内容"}'
```

删除某条记录：

```bash
curl -X DELETE http://localhost:5001/api/messages/1
```

> 在 Windows PowerShell 5.1 中，参数里的双引号会被丢掉，Flask 收到的是非法 JSON。
> 这种情况请把 JSON 中的引号写成 `\"`：
>
> ```powershell
> curl.exe -X POST http://localhost:5001/api/messages -H "Content-Type: application/json" --data-raw '{\"message\":\"你好\"}'
> ```
>
> 或者改用 PowerShell 原生命令，避免手工拼接引号：
>
> ```powershell
> $body = @{ message = "你好" } | ConvertTo-Json -Compress
> Invoke-RestMethod -Uri "http://localhost:5001/api/messages" -Method Post -ContentType "application/json" -Body $body
> ```

## 选做功能

本版本未实现 JSON 文件持久化和多会话功能：聊天记录只保存在内存中，Flask 重启后即清空；每次问答是一条彼此独立的记录，不携带历史上下文。

# AI 聊天助手

一个基于 Flask + DeepSeek API 的最小 AI 聊天 Web 应用。前端由原生 HTML / CSS / JavaScript 编写并由 Flask 同源提供；后端提供聊天记录的增删改查 API，回复由 DeepSeek 大模型真实生成。API Key 只保存在后端的 `.env` 文件中，不进入 Git、源代码或浏览器。

## 项目功能

- 单页聊天界面：发送消息、查看历史记录
- 以“一次问答”为一条聊天记录（用户消息 + AI 回复），支持修改与删除
- AI 回复由 DeepSeek（`deepseek-chat` 模型）生成
- 删除操作有两段式页面内确认；所有错误与状态反馈均通过页面内元素展示，不使用浏览器弹窗
- 数据保存在 Flask 进程内存中，服务重启后清空（未启用持久化）

## 环境要求

- Python 3.10+
- 一个 DeepSeek API Key（在 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请）

## 安装依赖

在仓库根目录 `isse-labs/` 下执行：

```bash
cd lab2/别克扎提·拜别提-2500016663
python -m pip install -r requirements.txt
```

依赖包括 `flask`（Web 框架）、`python-dotenv`（读取 `.env`）、`requests`（调用 DeepSeek API）。

## 配置：从 .env.example 创建本地 .env

1. 将 `.env.example` 复制为同目录下的 `.env`：

   ```bash
   cp .env.example .env        # bash
   Copy-Item .env.example .env # PowerShell
   ```

2. 编辑 `.env`，把 `your_api_key_here` 替换为你的真实 DeepSeek API Key；
3. `.env` 已被 `.gitignore` 忽略，不会被提交到仓库；请勿把真实 Key 写入任何源代码文件。

## 启动 Flask

```bash
python app.py
```

服务启动后监听 `5001` 端口（`http://127.0.0.1:5001`）。

## 浏览器访问

```text
http://localhost:5001/
```

## API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/hello` | 健康检查，返回 `{"message":"你好"}` |
| POST | `/api/messages` | 创建一条记录，请求体 `{"message":"..."}`；`reply` 由 DeepSeek 生成；成功返回 `201` 和完整记录 |
| GET | `/api/messages` | 返回全部聊天记录 |
| PATCH | `/api/messages/<id>` | 修改指定记录的 `message` 字段 |
| DELETE | `/api/messages/<id>` | 删除指定记录，成功返回 `204` |

错误情况（`message` 为空、id 不存在、服务器缺少 Key、DeepSeek 调用失败）分别返回 `400` / `404` / `500` / `502`，并附带 JSON 格式的 `error` 说明。

## API 测试示例

```bash
# 健康检查
curl http://localhost:5001/api/hello

# 创建一条消息（返回值包含 DeepSeek 生成的 reply）
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Please introduce Peking University in one sentence"}'
```

> 提示：部分中文 Windows 终端使用 GBK 编码，用 curl 发送含中文的 JSON 可能导致后端解析失败。建议用英文消息做 curl 测试，中文消息直接在浏览器页面中发送。

## 选做功能

未实现选做任务（JSON 文件持久化、多会话多轮对话）。

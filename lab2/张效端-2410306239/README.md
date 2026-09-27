# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：Flask 后端 + 原生前端，接入 DeepSeek API 实现真实 AI 回复，支持多会话与多轮对话。

## 项目结构

- `app.py`：Flask 后端
- `frontend/`：前端页面（HTML + CSS + JavaScript）
- `data/conversations.json`：会话与聊天记录持久化文件

## 数据结构与持久化

会话保存在 `data/conversations.json`，文件内容为一个 JSON 数组，每个会话的结构：

```json
{
  "id": 1,
  "title": "会话标题",
  "messages": [
    {"id": 1, "message": "用户输入", "reply": "AI 回复"}
  ]
}
```

- Flask 启动时读取该文件；文件不存在或内容异常时从空数据开始
- 每次创建、修改、删除会话或发送消息后立即写回文件
- 会话 id 与消息 id 都从已有最大 id + 1 续接，不与已有记录冲突

## API 设计

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/api/conversations` | 创建会话 |
| GET | `/api/conversations` | 查看全部会话 |
| GET | `/api/conversations/<id>` | 查看指定会话（含消息） |
| PATCH | `/api/conversations/<id>` | 重命名会话 |
| DELETE | `/api/conversations/<id>` | 删除会话 |
| POST | `/api/conversations/<id>/messages` | 在会话中发送消息 |
| GET | `/api/hello` | 连通性测试 |

## 多轮对话上下文

在某个会话中发送新消息时，后端把该会话的历史消息按 `user`/`assistant` 角色依次拼入请求的 `messages` 数组，最后附上本次新问题，一起发给 DeepSeek；模型返回的文本作为 `reply` 存入该会话。DeepSeek API 本身无状态，"记忆"由后端在每次请求时重建上下文来实现。

## 快速开始

（安装依赖、配置与启动方式的完整说明将在开发完成后补充。）

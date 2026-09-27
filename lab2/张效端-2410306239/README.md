# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：Flask 后端 + 原生前端，接入 DeepSeek API 实现真实 AI 回复。

## 项目结构

- `app.py`：Flask 后端
- `frontend/`：前端页面（HTML + CSS + JavaScript）
- `data/messages.json`：聊天记录持久化文件

## 数据持久化

聊天记录保存在 `data/messages.json`，文件内容为一个 JSON 数组，每个元素的结构：

```json
{"id": 1, "message": "用户输入", "reply": "AI 回复"}
```

- Flask 启动时读取该文件；文件不存在或内容异常时从空数据开始
- 每次创建、修改、删除消息后立即写回文件
- 新记录 ID 从已有最大 ID + 1 续接，不与已有记录冲突

## 快速开始

（安装依赖、配置与启动方式的完整说明将在开发完成后补充。）


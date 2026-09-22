# AI 聊天 Web 应用

## 项目简介

这是一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。前端负责展示聊天界面并调用后端 API，后端负责管理聊天记录并请求 AI 服务。

## 数据持久化

聊天记录保存在 `data/messages.json` 中。文件最外层是 JSON 数组，每条记录是包含 `id`、`message` 和 `reply` 的 JSON 对象。创建、修改或删除记录后，后端会立即将最新数据写回该文件；Flask 启动时会读取它，因此记录可以跨重启保留。

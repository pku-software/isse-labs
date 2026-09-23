# AI Chat Web Application

一个基于 Flask、HTML、CSS 和 JavaScript 构建的 AI 聊天 Web 应用。

## JSON 持久化

聊天记录保存在 `data/messages.json`。文件最外层是一个数组，每项为包含 `id`、`message` 和 `reply` 的对象。Flask 启动时读取该文件，并在创建、修改或删除记录后立即写回。

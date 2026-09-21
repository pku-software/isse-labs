# AI 聊天 Web 应用

一个最小但完整的网页聊天应用：前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask
并监听 `5001` 端口；前端通过 `fetch()` 调用自己的 Flask API，Flask 再调用 DeepSeek API
生成回复。聊天记录以「一次问答」为一条记录，支持创建、查看、修改和删除。

## 目录结构

- `app.py`：Flask 后端入口
- `frontend/index.html`、`frontend/style.css`、`frontend/app.js`：前端页面、样式与脚本
- `.env.example`：环境变量示例文件（只包含占位符）
- `requirements.txt`：Python 依赖列表
- `data/`：聊天记录 JSON 持久化目录（选做功能启用后才会出现）

## 安装依赖

（搭建完成后补全）

## 配置

（搭建完成后补全：如何从 `.env.example` 创建 `.env` 并填入 API Key）

## 启动

（搭建完成后补全：启动 Flask 的步骤）

## 浏览器访问

（搭建完成后补全：访问地址 `http://localhost:5001/`）

## API 说明

（搭建完成后补全：各接口的路径、方法、请求与响应示例）

## 选做功能

（如有完成再补全）

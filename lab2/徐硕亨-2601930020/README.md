# AI 聊天 Web 应用

本项目是一个基于 Flask 和原生 JavaScript 搭建的轻量級 AI 聊天 Web 應用，支援前後端分離通訊、聊天紀錄的 CRUD（增刪改查）以及接入 DeepSeek 大模型進行對話。

## 功能介紹
- 前端使用原生 HTML + CSS + JavaScript 構建聊天介面。
- 後端使用 Python Flask 提供 RESTful API 服務。
- 支援對話訊息的建立、讀取、修改與刪除（CRUD）。
- 整合 DeepSeek API 進行模型對話。

## 環境依賴與安裝
```bash
pip install -r requirements.txt
```

## 環境變數配置
1. 複製設定檔範本：
   ```bash
   cp .env.example .env
   ```
2. 在 `.env` 中填寫您的 DeepSeek API Key：
   ```text
   DEEPSEEK_API_KEY=your_api_key_here
   ```

## 啟動方式
```bash
python app.py
```
啟動後，瀏覽器造訪位址：
`http://localhost:5001/`

## API 規格說明
- `GET /api/hello`：測試後端連線狀態
- `GET /api/messages`：取得所有聊天紀錄
- `POST /api/messages`：新增一筆聊天紀錄
- `PATCH /api/messages/<id>`：修改指定 ID 的聊天內容
- `DELETE /api/messages/<id>`：刪除指定 ID 的聊天紀錄

## API 測試範例
```bash
curl http://localhost:5001/api/hello
```

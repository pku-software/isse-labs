"use strict";

const API_URL = "/api/messages";

const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const pageFeedback = document.querySelector("#page-feedback");
const connectionStatus = document.querySelector("#connection-status");

let messages = [];
let editingId = null;
let deletingId = null;

function setFeedback(text, kind = "info") {
  pageFeedback.textContent = text;
  pageFeedback.dataset.kind = kind;
}

function setConnectionStatus(text, state) {
  connectionStatus.textContent = text;
  connectionStatus.dataset.state = state;
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `请求失败（HTTP ${response.status}）`);
  }

  return data;
}

function createRecordElement(record) {
  const article = document.createElement("article");
  article.className = "chat-record";
  article.dataset.messageId = record.id;
  article.innerHTML = `
    <div class="message-row message-row--user">
      <div class="message-bubble message-bubble--user">
        <span class="message-label">你</span>
        <p class="user-message"></p>
      </div>
    </div>
    <div class="message-row message-row--assistant">
      <div class="avatar" aria-hidden="true">AI</div>
      <div class="message-bubble message-bubble--assistant">
        <span class="message-label">助手</span>
        <p class="assistant-message"></p>
      </div>
    </div>
    <div class="record-actions" aria-label="记录操作">
      <button class="text-button" type="button" data-action="edit">修改</button>
      <button class="text-button text-button--danger" type="button" data-action="delete">删除</button>
    </div>
  `;

  article.querySelector(".user-message").textContent = record.message;
  article.querySelector(".assistant-message").textContent = record.reply;

  if (editingId === record.id) {
    const panel = document.createElement("div");
    panel.className = "inline-panel";
    panel.innerHTML = `
      <label for="edit-message-${record.id}">修改你的消息</label>
      <textarea id="edit-message-${record.id}" rows="3"></textarea>
      <div class="inline-actions">
        <button class="action-button action-button--secondary" type="button" data-action="cancel">取消</button>
        <button class="action-button" type="button" data-action="save">保存</button>
      </div>
    `;
    panel.querySelector("textarea").value = record.message;
    article.append(panel);
  }

  if (deletingId === record.id) {
    const panel = document.createElement("div");
    panel.className = "inline-panel inline-panel--danger";
    panel.innerHTML = `
      <p>确定删除这条聊天记录吗？</p>
      <div class="inline-actions">
        <button class="action-button action-button--secondary" type="button" data-action="cancel">取消</button>
        <button class="action-button action-button--danger" type="button" data-action="confirm-delete">确认删除</button>
      </div>
    `;
    article.append(panel);
  }

  return article;
}

function renderMessages() {
  messageList.replaceChildren();

  if (messages.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "还没有聊天记录，发送第一条消息吧。";
    messageList.append(emptyState);
    return;
  }

  messages.forEach((record) => {
    messageList.append(createRecordElement(record));
  });
}

async function loadMessages() {
  try {
    messages = await apiRequest(API_URL);
    renderMessages();
    setConnectionStatus("API 已连接", "success");
    setFeedback("聊天记录已加载。", "success");
  } catch (error) {
    messageList.innerHTML = '<p class="empty-state">无法加载聊天记录。</p>';
    setConnectionStatus("连接失败", "error");
    setFeedback(error.message, "error");
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();

  if (!message) {
    setFeedback("请输入消息后再发送。", "error");
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  setFeedback("正在发送……");

  try {
    const record = await apiRequest(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messages.push(record);
    renderMessages();
    messageForm.reset();
    messageInput.focus();
    setFeedback("消息已创建。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    sendButton.disabled = false;
  }
});

messageList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  const article = event.target.closest(".chat-record");
  if (!button || !article) {
    return;
  }

  const messageId = Number(article.dataset.messageId);
  const action = button.dataset.action;

  if (action === "edit") {
    editingId = messageId;
    deletingId = null;
    renderMessages();
    messageList.querySelector(`#edit-message-${messageId}`).focus();
    return;
  }

  if (action === "delete") {
    deletingId = messageId;
    editingId = null;
    renderMessages();
    return;
  }

  if (action === "cancel") {
    editingId = null;
    deletingId = null;
    renderMessages();
    return;
  }

  button.disabled = true;

  try {
    if (action === "save") {
      const editedMessage = article.querySelector("textarea").value.trim();
      if (!editedMessage) {
        setFeedback("修改后的消息不能为空。", "error");
        article.querySelector("textarea").focus();
        return;
      }

      const updatedRecord = await apiRequest(`${API_URL}/${messageId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: editedMessage }),
      });
      messages = messages.map((record) =>
        record.id === messageId ? updatedRecord : record,
      );
      editingId = null;
      renderMessages();
      setFeedback("消息已修改。", "success");
    }

    if (action === "confirm-delete") {
      await apiRequest(`${API_URL}/${messageId}`, { method: "DELETE" });
      messages = messages.filter((record) => record.id !== messageId);
      deletingId = null;
      renderMessages();
      setFeedback("聊天记录已删除。", "success");
    }
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

loadMessages();

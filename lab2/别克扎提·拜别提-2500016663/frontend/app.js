// AI 聊天助手前端交互逻辑
//
// 全部数据操作都通过 fetch() + 相对 URL 调用同源的 Flask API：
//   GET    /api/messages        读取全部记录
//   POST   /api/messages        新建记录
//   PATCH  /api/messages/<id>   修改记录
//   DELETE /api/messages/<id>   删除记录

// ===== DOM 引用 =====
const chatMessages = document.getElementById("chat-messages");
const emptyHint = document.getElementById("empty-hint");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusBar = document.getElementById("status-bar");

// ===== 页面内状态数据（唯一数据来源，渲染始终基于它） =====
let messages = [];

// ===== 页面内状态提示（替代 alert/confirm 等浏览器弹窗） =====
let statusTimer = null;

function showStatus(text, type = "error") {
  statusBar.textContent = text;
  statusBar.className = `status-bar status-${type}`;
  statusBar.hidden = false;
  clearTimeout(statusTimer);
  statusTimer = setTimeout(() => {
    statusBar.hidden = true;
  }, 3000);
}

// ===== 渲染 =====

function createButton(text, className, onClick) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = className;
  btn.textContent = text;
  btn.addEventListener("click", onClick);
  return btn;
}

function createRecordElement(record) {
  const article = document.createElement("article");
  article.className = "chat-record";
  article.dataset.id = record.id;

  const content = document.createElement("div");
  content.className = "record-content";

  // 用户消息行
  const messageRow = document.createElement("div");
  messageRow.className = "record-message";
  const messageLabel = document.createElement("span");
  messageLabel.className = "role-label";
  messageLabel.textContent = "我";
  const messageBubble = document.createElement("div");
  messageBubble.className = "bubble bubble-user";
  const messageText = document.createElement("p");
  messageText.className = "message-text";
  // 使用 textContent 写入用户输入，天然防止其被当作 HTML 执行
  messageText.textContent = record.message;
  messageBubble.appendChild(messageText);
  messageRow.append(messageLabel, messageBubble);

  // AI 回复行
  const replyRow = document.createElement("div");
  replyRow.className = "record-reply";
  const replyLabel = document.createElement("span");
  replyLabel.className = "role-label";
  replyLabel.textContent = "AI";
  const replyBubble = document.createElement("div");
  replyBubble.className = "bubble bubble-ai";
  const replyText = document.createElement("p");
  replyText.className = "reply-text";
  replyText.textContent = record.reply;
  replyBubble.appendChild(replyText);
  replyRow.append(replyLabel, replyBubble);

  content.append(messageRow, replyRow);

  // 操作按钮
  const actions = document.createElement("div");
  actions.className = "record-actions";
  actions.appendChild(
    createButton("修改", "btn btn-edit", (event) => {
      startEdit(record.id, event.currentTarget.closest(".chat-record"));
    })
  );
  actions.appendChild(
    createButton("删除", "btn btn-delete", (event) => {
      deleteRecord(record.id, event.currentTarget);
    })
  );

  article.append(content, actions);
  return article;
}

function renderAll() {
  chatMessages.querySelectorAll(".chat-record").forEach((el) => el.remove());
  emptyHint.hidden = messages.length > 0;
  const fragment = document.createDocumentFragment();
  for (const record of messages) {
    fragment.appendChild(createRecordElement(record));
  }
  chatMessages.appendChild(fragment);
}

// ===== API 调用 =====

async function loadMessages() {
  try {
    const res = await fetch("/api/messages");
    if (!res.ok) {
      showStatus("加载聊天记录失败");
      return;
    }
    messages = await res.json();
    renderAll();
  } catch (err) {
    showStatus("无法连接后端，请确认 Flask 已在 5001 端口运行");
  }
}

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) {
    showStatus("请输入消息内容");
    return;
  }
  sendButton.disabled = true;
  try {
    const res = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    if (!res.ok) {
      showStatus(`发送失败：${data.error || res.status}`);
      return;
    }
    messages.push(data);
    messageInput.value = "";
    renderAll();
  } catch (err) {
    showStatus("网络错误，发送失败");
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

function startEdit(recordId, article) {
  const record = messages.find((m) => m.id === recordId);
  if (!record) return;

  const bubble = article.querySelector(".bubble-user");
  const actions = article.querySelector(".record-actions");
  const messageRow = article.querySelector(".record-message");

  async function saveEdit() {
    const newText = input.value.trim();
    if (!newText) {
      showStatus("消息内容不能为空");
      return;
    }
    try {
      const res = await fetch(`/api/messages/${recordId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newText }),
      });
      const data = await res.json();
      if (!res.ok) {
        showStatus(`修改失败：${data.error || res.status}`);
        return;
      }
      const index = messages.findIndex((m) => m.id === recordId);
      if (index !== -1) messages[index] = data;
      renderAll();
      showStatus("修改成功", "success");
    } catch (err) {
      showStatus("网络错误，修改失败");
    }
  }

  function cancelEdit() {
    editRow.remove();
    bubble.hidden = false;
    actions.hidden = false;
  }

  // 编辑行：输入框 + 保存 / 取消
  const editRow = document.createElement("div");
  editRow.className = "edit-row";
  const input = document.createElement("input");
  input.type = "text";
  input.className = "edit-input";
  input.value = record.message;
  editRow.appendChild(input);
  editRow.appendChild(createButton("保存", "btn btn-save", saveEdit));
  editRow.appendChild(createButton("取消", "btn btn-cancel", cancelEdit));

  bubble.hidden = true;
  actions.hidden = true;
  messageRow.appendChild(editRow);
  input.focus();

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") saveEdit();
    if (event.key === "Escape") cancelEdit();
  });
}

// 两段式删除确认：第一次点击只把按钮置为“确认删除？”，再次点击才真正删除
let deleteConfirmTimer = null;

function resetDeleteButton(button) {
  button.classList.remove("armed");
  button.textContent = "删除";
}

async function deleteRecord(recordId, button) {
  if (!button.classList.contains("armed")) {
    document.querySelectorAll(".btn-delete.armed").forEach(resetDeleteButton);
    button.classList.add("armed");
    button.textContent = "确认删除？";
    clearTimeout(deleteConfirmTimer);
    deleteConfirmTimer = setTimeout(() => resetDeleteButton(button), 3000);
    return;
  }

  clearTimeout(deleteConfirmTimer);
  try {
    const res = await fetch(`/api/messages/${recordId}`, { method: "DELETE" });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      showStatus(`删除失败：${data.error || res.status}`);
      return;
    }
    messages = messages.filter((m) => m.id !== recordId);
    renderAll();
    showStatus("已删除", "success");
  } catch (err) {
    showStatus("网络错误，删除失败");
  }
}

// ===== 事件绑定与初始化 =====

sendButton.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendMessage();
});

// 页面打开时加载已有记录
loadMessages();

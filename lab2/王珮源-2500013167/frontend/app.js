// 前端脚本：渲染聊天记录，并通过 fetch() 调用同一个 Flask 服务上的 API。
// 输入、确认和错误提示全部显示在页面里，不使用 alert()/prompt()/confirm()。

const API_URL = "/api/messages";

const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusText = document.getElementById("status-text");

let messages = [];       // 与服务端同步的聊天记录
let editingId = null;    // 正在修改的记录 id
let confirmingId = null; // 正在等待删除确认的记录 id
let busy = false;        // 是否有请求正在进行

function setStatus(text, isError = false) {
  statusText.textContent = text;
  statusText.classList.toggle("error", isError);
}

function setBusy(value) {
  busy = value;
  sendButton.disabled = value;
}

// ---------- 与后端通信 ----------

async function requestJSON(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const reason = data && data.error ? data.error : `HTTP ${response.status}`;
    throw new Error(reason);
  }
  return data;
}

async function loadMessages() {
  setStatus("正在加载聊天记录…");
  try {
    messages = await requestJSON(API_URL);
    setStatus("");
  } catch (error) {
    setStatus(`加载失败：${error.message}`, true);
  }
  render();
}

async function createMessage(text) {
  setBusy(true);
  setStatus("发送中…");
  try {
    const record = await requestJSON(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    messages.push(record);
    messageInput.value = "";
    setStatus(`已创建记录 #${record.id}`);
  } catch (error) {
    setStatus(`发送失败：${error.message}`, true);
  } finally {
    setBusy(false);
    render();
  }
}

async function saveMessage(id, text) {
  try {
    const record = await requestJSON(`${API_URL}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    messages = messages.map((item) => (item.id === id ? record : item));
    editingId = null;
    setStatus(`已更新记录 #${id}`);
  } catch (error) {
    setStatus(`修改失败：${error.message}`, true);
  }
  render();
}

async function removeMessage(id) {
  try {
    await requestJSON(`${API_URL}/${id}`, { method: "DELETE" });
    messages = messages.filter((item) => item.id !== id);
    confirmingId = null;
    if (editingId === id) {
      editingId = null;
    }
    setStatus(`已删除记录 #${id}`);
  } catch (error) {
    setStatus(`删除失败：${error.message}`, true);
  }
  render();
}

// ---------- 页面渲染 ----------

function roleSpan(text) {
  const span = document.createElement("span");
  span.className = "role";
  span.textContent = text;
  return span;
}

function actionButton(label, action) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "action-link";
  button.dataset.action = action;
  button.textContent = label;
  return button;
}

function renderActions(record) {
  const actions = document.createElement("div");
  actions.className = "message-actions";

  if (confirmingId === record.id) {
    const question = document.createElement("span");
    question.className = "confirm-text";
    question.textContent = "确定删除这条记录？";

    const confirmButton = actionButton("确认删除", "confirm-delete");
    confirmButton.addEventListener("click", () => removeMessage(record.id));

    const cancelButton = actionButton("取消", "cancel-delete");
    cancelButton.addEventListener("click", () => {
      confirmingId = null;
      setStatus("");
      render();
    });

    actions.append(question, confirmButton, cancelButton);
    return actions;
  }

  const editButton = actionButton("修改", "edit");
  editButton.addEventListener("click", () => {
    editingId = record.id;
    confirmingId = null;
    setStatus("");
    render();
  });

  const deleteButton = actionButton("删除", "delete");
  deleteButton.addEventListener("click", () => {
    confirmingId = record.id;
    editingId = null;
    setStatus("");
    render();
  });

  actions.append(editButton, deleteButton);
  return actions;
}

function renderEditForm(record) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-edit";

  const textarea = document.createElement("textarea");
  textarea.className = "edit-input";
  textarea.rows = 2;
  textarea.value = record.message;
  textarea.setAttribute("aria-label", `修改记录 #${record.id}`);

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const saveButton = actionButton("保存", "save");
  saveButton.addEventListener("click", () => saveMessage(record.id, textarea.value));

  const cancelButton = actionButton("取消", "cancel-edit");
  cancelButton.addEventListener("click", () => {
    editingId = null;
    setStatus("");
    render();
  });

  actions.append(saveButton, cancelButton);
  wrapper.append(textarea, actions);

  // 渲染完成后把光标放进编辑框
  requestAnimationFrame(() => textarea.focus());
  return wrapper;
}

function renderMessage(record) {
  const article = document.createElement("article");
  article.className = "message";
  article.dataset.id = String(record.id);

  const userBlock = document.createElement("div");
  userBlock.className = "user-block";

  if (editingId === record.id) {
    userBlock.append(renderEditForm(record));
  } else {
    const bubble = document.createElement("p");
    bubble.className = "bubble bubble-user";
    bubble.append(roleSpan("我"), document.createTextNode(record.message));
    userBlock.append(bubble, renderActions(record));
  }

  const reply = document.createElement("p");
  reply.className = "bubble bubble-ai";
  reply.append(roleSpan("AI"), document.createTextNode(record.reply));

  article.append(userBlock, reply);
  return article;
}

function render() {
  chatWindow.replaceChildren();

  if (messages.length === 0) {
    const hint = document.createElement("p");
    hint.className = "empty-hint";
    hint.textContent = "暂无聊天记录";
    chatWindow.append(hint);
    return;
  }

  for (const record of messages) {
    chatWindow.append(renderMessage(record));
  }
}

// ---------- 事件绑定 ----------

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (busy) {
    return;
  }
  if (!text) {
    setStatus("请先输入内容再发送。", true);
    return;
  }
  createMessage(text);
});

// 输入框里按 Enter 直接发送，Shift+Enter 换行
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

loadMessages();

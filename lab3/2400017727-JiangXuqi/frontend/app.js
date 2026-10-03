// 前端通过 fetch() 调用同一个 Flask 服务的 API。
// 这里用的是相对 URL，浏览器会自动基于当前页面地址解析。

const MESSAGES_API = "/api/messages";

const listEl = document.getElementById("message-list");
const formEl = document.getElementById("composer");
const inputEl = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusEl = document.getElementById("status");

const state = {
  messages: [],
  editingId: null,
  editingText: "",
  confirmingId: null,
  sending: false,
};

// ---------- 通用工具 ----------

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data && data.error ? data.error : `请求失败（HTTP ${response.status}）`;
    throw new Error(detail);
  }

  return data;
}

function setStatus(text, type) {
  statusEl.textContent = text;
  statusEl.className = type === "error" ? "status status-error" : "status";
  statusEl.hidden = !text;
}

// ---------- 渲染 ----------

function render() {
  listEl.textContent = "";

  if (state.messages.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "还没有聊天记录，在下面输入一条消息试试。";
    listEl.appendChild(empty);
    return;
  }

  state.messages.forEach((item) => {
    listEl.appendChild(renderItem(item));
  });
}

function renderItem(item) {
  const wrapper = document.createElement("article");
  wrapper.className = "message";
  wrapper.dataset.id = item.id;

  const editing = state.editingId === item.id;

  if (editing) {
    wrapper.appendChild(renderEditBox(item));
  } else {
    const userBubble = document.createElement("p");
    userBubble.className = "bubble bubble-user";
    userBubble.textContent = item.message;
    wrapper.appendChild(userBubble);
  }

  const replyBubble = document.createElement("p");
  replyBubble.className = "bubble bubble-reply";
  replyBubble.textContent = item.reply;
  wrapper.appendChild(replyBubble);

  if (editing) {
    return wrapper;
  }

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.className = "link-button";
  editButton.textContent = "修改";
  editButton.addEventListener("click", () => startEdit(item));

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "link-button danger";
  deleteButton.textContent = "删除";
  deleteButton.addEventListener("click", () => {
    state.confirmingId = item.id;
    setStatus("");
    render();
  });

  actions.append(editButton, deleteButton);
  wrapper.appendChild(actions);

  if (state.confirmingId === item.id) {
    wrapper.appendChild(renderDeleteConfirm());
  }

  return wrapper;
}

function renderEditBox(item) {
  const box = document.createElement("div");
  box.className = "message-edit";

  const editInput = document.createElement("input");
  editInput.className = "message-input";
  editInput.type = "text";
  editInput.value = state.editingText;
  editInput.addEventListener("input", () => {
    state.editingText = editInput.value;
  });
  editInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveEdit(item.id);
    } else if (event.key === "Escape") {
      cancelEdit();
    }
  });

  const saveButton = document.createElement("button");
  saveButton.type = "button";
  saveButton.className = "button button-primary button-small";
  saveButton.textContent = "保存";
  saveButton.addEventListener("click", () => saveEdit(item.id));

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "button button-ghost button-small";
  cancelButton.textContent = "取消";
  cancelButton.addEventListener("click", cancelEdit);

  box.append(editInput, saveButton, cancelButton);
  return box;
}

function renderDeleteConfirm() {
  const box = document.createElement("div");
  box.className = "message-confirm";

  const text = document.createElement("span");
  text.textContent = "确定删除这条记录吗？";

  const confirmButton = document.createElement("button");
  confirmButton.type = "button";
  confirmButton.className = "link-button danger";
  confirmButton.textContent = "确定删除";
  confirmButton.addEventListener("click", () => removeMessage(state.confirmingId));

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "link-button";
  cancelButton.textContent = "取消";
  cancelButton.addEventListener("click", () => {
    state.confirmingId = null;
    render();
  });

  box.append(text, confirmButton, cancelButton);
  return box;
}

// ---------- 数据操作 ----------

async function loadMessages() {
  try {
    state.messages = await api(MESSAGES_API);
    setStatus("");
  } catch (error) {
    setStatus(`加载失败：${error.message}`, "error");
  }
  render();
}

async function sendMessage() {
  const text = inputEl.value.trim();

  if (!text) {
    setStatus("请输入消息内容。", "error");
    inputEl.focus();
    return;
  }

  if (state.sending) {
    return;
  }

  state.sending = true;
  sendButton.disabled = true;
  setStatus("正在发送…");

  try {
    const record = await api(MESSAGES_API, {
      method: "POST",
      body: JSON.stringify({ message: text }),
    });
    state.messages.push(record);
    inputEl.value = "";
    setStatus("已发送。");
  } catch (error) {
    setStatus(`发送失败：${error.message}`, "error");
  } finally {
    state.sending = false;
    sendButton.disabled = false;
  }

  render();
  inputEl.focus();
}

function startEdit(item) {
  state.editingId = item.id;
  state.editingText = item.message;
  state.confirmingId = null;
  setStatus("");
  render();

  const editInput = listEl.querySelector(`.message[data-id="${item.id}"] .message-input`);
  if (editInput) {
    editInput.focus();
    editInput.setSelectionRange(editInput.value.length, editInput.value.length);
  }
}

function cancelEdit() {
  state.editingId = null;
  state.editingText = "";
  render();
}

async function saveEdit(id) {
  const text = state.editingText.trim();

  if (!text) {
    setStatus("消息内容不能为空。", "error");
    return;
  }

  try {
    const updated = await api(`${MESSAGES_API}/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ message: text }),
    });
    state.messages = state.messages.map((item) => (item.id === id ? updated : item));
    state.editingId = null;
    state.editingText = "";
    setStatus("修改成功。");
  } catch (error) {
    setStatus(`修改失败：${error.message}`, "error");
  }

  render();
}

async function removeMessage(id) {
  try {
    await api(`${MESSAGES_API}/${id}`, { method: "DELETE" });
    state.messages = state.messages.filter((item) => item.id !== id);
    state.confirmingId = null;
    if (state.editingId === id) {
      state.editingId = null;
      state.editingText = "";
    }
    setStatus("已删除。");
  } catch (error) {
    setStatus(`删除失败：${error.message}`, "error");
  }

  render();
}

// ---------- 启动 ----------

document.addEventListener("DOMContentLoaded", () => {
  formEl.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage();
  });

  loadMessages();
});

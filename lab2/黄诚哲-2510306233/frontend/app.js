const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const editArea = document.getElementById("edit-area");
const editInput = document.getElementById("edit-input");
const editSave = document.getElementById("edit-save");
const editCancel = document.getElementById("edit-cancel");
const editFeedback = document.getElementById("edit-feedback");
const statusEl = document.getElementById("status");

let editingId = null;

async function loadMessages() {
  const res = await fetch("/api/messages");
  const data = await res.json();
  renderMessages(data);
}

function renderMessages(records) {
  messagesEl.innerHTML = "";
  for (const record of records) {
    messagesEl.appendChild(createRecordNode(record));
  }
}

function createRecordNode(record) {
  const wrapper = document.createElement("div");
  wrapper.className = "record";

  const user = document.createElement("div");
  user.className = "message user";
  const userText = document.createElement("div");
  userText.className = "message-text";
  userText.textContent = record.message;
  user.appendChild(userText);

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editBtn = document.createElement("button");
  editBtn.textContent = "修改";
  editBtn.addEventListener("click", () => startEdit(record));

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "删除";
  deleteBtn.addEventListener("click", () => deleteMessage(record.id));

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);
  user.appendChild(actions);

  const reply = document.createElement("div");
  reply.className = "message reply";
  const replyText = document.createElement("div");
  replyText.className = "message-text";
  replyText.textContent = record.reply;
  reply.appendChild(replyText);

  wrapper.appendChild(user);
  wrapper.appendChild(reply);
  return wrapper;
}

async function sendMessage() {
  const message = inputEl.value.trim();
  if (!message) {
    showFeedback("请输入消息内容");
    return;
  }
  const res = await fetch("/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const err = await res.json();
    showFeedback(err.error || "发送失败");
    return;
  }
  inputEl.value = "";
  await loadMessages();
}

function startEdit(record) {
  editingId = record.id;
  editInput.value = record.message;
  editArea.hidden = false;
  editInput.focus();
}

function cancelEdit() {
  editingId = null;
  editInput.value = "";
  editArea.hidden = true;
  editFeedback.textContent = "";
}

async function saveEdit() {
  if (editingId === null) return;
  const message = editInput.value.trim();
  if (!message) {
    editFeedback.textContent = "内容不能为空";
    return;
  }
  const res = await fetch(`/api/messages/${editingId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const err = await res.json();
    editFeedback.textContent = err.error || "修改失败";
    return;
  }
  cancelEdit();
  await loadMessages();
}

async function deleteMessage(id) {
  const res = await fetch(`/api/messages/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json();
    showFeedback(err.error || "删除失败");
    return;
  }
  await loadMessages();
}

function showFeedback(text) {
  statusEl.textContent = text;
  statusEl.hidden = false;
  setTimeout(() => {
    statusEl.textContent = "";
    statusEl.hidden = true;
  }, 3000);
}

sendButton.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});
editSave.addEventListener("click", saveEdit);
editCancel.addEventListener("click", cancelEdit);

loadMessages();

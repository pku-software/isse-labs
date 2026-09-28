const conversationListEl = document.getElementById("conversation-list");
const conversationTitleEl = document.getElementById("conversation-title");
const messagesEl = document.getElementById("messages");
const newConversationBtn = document.getElementById("new-conversation");
const conversationForm = document.getElementById("conversation-form");
const conversationTitleInput = document.getElementById(
  "conversation-title-input"
);
const conversationFormSave = document.getElementById("conversation-form-save");
const conversationFormCancel = document.getElementById(
  "conversation-form-cancel"
);
const inputEl = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const editArea = document.getElementById("edit-area");
const editInput = document.getElementById("edit-input");
const editSave = document.getElementById("edit-save");
const editDelete = document.getElementById("edit-delete");
const editCancel = document.getElementById("edit-cancel");
const editFeedback = document.getElementById("edit-feedback");
const statusEl = document.getElementById("status");

let currentConversationId = null;
let editingMessageId = null;
let conversationFormMode = null;
let renameTargetId = null;

async function loadConversations() {
  const res = await fetch("/api/conversations");
  const data = await res.json();
  renderConversationList(data);
}

function renderConversationList(conversations) {
  conversationListEl.innerHTML = "";
  for (const conversation of conversations) {
    const item = document.createElement("li");
    item.className = "conversation-item";
    if (conversation.id === currentConversationId) {
      item.classList.add("active");
    }

    const title = document.createElement("div");
    title.className = "conversation-title-text";
    title.textContent = conversation.title;
    item.appendChild(title);

    const actions = document.createElement("div");
    actions.className = "conversation-actions";

    const renameBtn = document.createElement("button");
    renameBtn.textContent = "重命名";
    renameBtn.addEventListener("click", () =>
      showConversationForm("rename", conversation)
    );

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "删除";
    deleteBtn.addEventListener("click", () => deleteConversation(conversation.id));

    actions.appendChild(renameBtn);
    actions.appendChild(deleteBtn);
    item.appendChild(actions);

    item.addEventListener("click", (e) => {
      if (e.target.tagName === "BUTTON") return;
      selectConversation(conversation.id);
    });

    conversationListEl.appendChild(item);
  }
}

async function selectConversation(id) {
  currentConversationId = id;
  const res = await fetch(`/api/conversations/${id}`);
  if (!res.ok) return;
  const conversation = await res.json();
  conversationTitleEl.textContent = conversation.title;
  renderMessages(conversation.messages);
  await loadConversations();
}

function renderMessages(messages) {
  messagesEl.innerHTML = "";
  for (const message of messages) {
    messagesEl.appendChild(createMessageNode(message));
  }
}

function createMessageNode(message) {
  const node = document.createElement("div");
  node.className = `message ${message.role}`;

  const text = document.createElement("div");
  text.className = "message-text";
  text.textContent = message.content;
  node.appendChild(text);

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editBtn = document.createElement("button");
  editBtn.textContent = "修改";
  editBtn.addEventListener("click", () => startEdit(message));

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "删除";
  deleteBtn.addEventListener("click", () => startDelete(message));

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);
  node.appendChild(actions);

  return node;
}

function showConversationForm(mode, conversation) {
  conversationFormMode = mode;
  conversationForm.hidden = false;
  if (mode === "rename") {
    renameTargetId = conversation.id;
    conversationTitleInput.value = conversation.title;
  } else {
    renameTargetId = null;
    conversationTitleInput.value = "";
  }
  conversationTitleInput.focus();
}

function hideConversationForm() {
  conversationForm.hidden = true;
  conversationFormMode = null;
  renameTargetId = null;
  conversationTitleInput.value = "";
}

async function submitConversationForm() {
  const title = conversationTitleInput.value.trim();
  if (!title) {
    showFeedback("会话名称不能为空");
    return;
  }
  if (conversationFormMode === "rename" && renameTargetId !== null) {
    await fetch(`/api/conversations/${renameTargetId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
  } else {
    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    const conversation = await res.json();
    currentConversationId = conversation.id;
    conversationTitleEl.textContent = conversation.title;
    renderMessages(conversation.messages);
  }
  hideConversationForm();
  await loadConversations();
}

async function deleteConversation(id) {
  const res = await fetch(`/api/conversations/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json();
    showFeedback(err.error || "删除失败");
    return;
  }
  if (currentConversationId === id) {
    currentConversationId = null;
    conversationTitleEl.textContent = "选择一个会话";
    messagesEl.innerHTML = "";
  }
  await loadConversations();
}

async function sendMessage() {
  if (currentConversationId === null) {
    showFeedback("请先选择或新建一个会话");
    return;
  }
  const message = inputEl.value.trim();
  if (!message) {
    showFeedback("请输入消息内容");
    return;
  }
  const res = await fetch(
    `/api/conversations/${currentConversationId}/messages`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    }
  );
  if (!res.ok) {
    const err = await res.json();
    showFeedback(err.error || "发送失败");
    return;
  }
  const conversation = await res.json();
  inputEl.value = "";
  renderMessages(conversation.messages);
  await loadConversations();
}

function startEdit(message) {
  editingMessageId = message.id;
  editInput.value = message.content;
  editInput.disabled = false;
  editSave.disabled = false;
  editArea.hidden = false;
  editInput.focus();
}

function startDelete(message) {
  editingMessageId = message.id;
  editInput.value = message.content;
  editInput.disabled = true;
  editSave.disabled = true;
  editArea.hidden = false;
}

function cancelEdit() {
  editingMessageId = null;
  editInput.value = "";
  editInput.disabled = false;
  editSave.disabled = false;
  editArea.hidden = true;
  editFeedback.textContent = "";
}

async function saveEdit() {
  if (editingMessageId === null) return;
  const content = editInput.value.trim();
  if (!content) {
    editFeedback.textContent = "内容不能为空";
    return;
  }
  const res = await fetch(
    `/api/conversations/${currentConversationId}/messages/${editingMessageId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    }
  );
  if (!res.ok) {
    const err = await res.json();
    editFeedback.textContent = err.error || "修改失败";
    return;
  }
  cancelEdit();
  await selectConversation(currentConversationId);
}

async function deleteMessage() {
  if (editingMessageId === null) return;
  const res = await fetch(
    `/api/conversations/${currentConversationId}/messages/${editingMessageId}`,
    { method: "DELETE" }
  );
  if (!res.ok) {
    const err = await res.json();
    editFeedback.textContent = err.error || "删除失败";
    return;
  }
  cancelEdit();
  await selectConversation(currentConversationId);
}

function showFeedback(text) {
  statusEl.textContent = text;
  statusEl.hidden = false;
  setTimeout(() => {
    statusEl.textContent = "";
    statusEl.hidden = true;
  }, 3000);
}

newConversationBtn.addEventListener("click", () =>
  showConversationForm("create")
);
conversationFormSave.addEventListener("click", submitConversationForm);
conversationFormCancel.addEventListener("click", hideConversationForm);
sendButton.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});
editSave.addEventListener("click", saveEdit);
editDelete.addEventListener("click", deleteMessage);
editCancel.addEventListener("click", cancelEdit);

loadConversations();

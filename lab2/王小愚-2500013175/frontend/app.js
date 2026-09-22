const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const feedback = document.querySelector("#feedback");
const submitButton = messageForm.querySelector("button[type='submit']");

let messages = [];
let editingId = null;
let deletingId = null;

function setFeedback(text = "", kind = "") {
  feedback.textContent = text;
  feedback.dataset.kind = kind;
}

function makeButton(label, className, action, id) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.dataset.action = action;
  button.dataset.id = id;
  button.textContent = label;
  return button;
}

function createMessageBubble(label, text, className) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${className}`;

  const badge = document.createElement("span");
  badge.className = "message-label";
  badge.textContent = label;

  const content = document.createElement("p");
  content.textContent = text;

  wrapper.append(badge, content);
  return wrapper;
}

function createEditPanel(record) {
  const panel = document.createElement("form");
  panel.className = "edit-panel";
  panel.dataset.id = record.id;

  const label = document.createElement("label");
  label.htmlFor = `edit-message-${record.id}`;
  label.textContent = "修改消息";

  const input = document.createElement("textarea");
  input.id = `edit-message-${record.id}`;
  input.name = "message";
  input.required = true;
  input.value = record.message;

  const actions = document.createElement("div");
  actions.className = "panel-actions";
  const cancel = makeButton("取消", "secondary-button", "cancel-edit", record.id);
  const save = document.createElement("button");
  save.type = "submit";
  save.className = "primary-button";
  save.textContent = "保存";
  actions.append(cancel, save);

  panel.append(label, input, actions);
  return panel;
}

function createDeletePanel(record) {
  const panel = document.createElement("div");
  panel.className = "delete-panel";

  const text = document.createElement("p");
  text.textContent = "确定删除这条聊天记录吗？";

  const actions = document.createElement("div");
  actions.className = "panel-actions";
  actions.append(
    makeButton("取消", "secondary-button", "cancel-delete", record.id),
    makeButton("确认删除", "danger-button", "confirm-delete", record.id),
  );

  panel.append(text, actions);
  return panel;
}

function renderMessages() {
  messageList.replaceChildren();

  if (messages.length === 0) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    emptyState.textContent = "还没有聊天记录，发送一条消息开始吧。";
    messageList.append(emptyState);
    return;
  }

  for (const record of messages) {
    const article = document.createElement("article");
    article.className = "chat-record";
    article.append(
      createMessageBubble("你", record.message, "user-message"),
      createMessageBubble("AI", record.reply, "assistant-message"),
    );

    const actions = document.createElement("div");
    actions.className = "record-actions";
    actions.setAttribute("aria-label", "记录操作");
    actions.append(
      makeButton("修改", "secondary-button", "edit", record.id),
      makeButton("删除", "danger-button", "delete", record.id),
    );
    article.append(actions);

    if (editingId === record.id) {
      article.append(createEditPanel(record));
    }
    if (deletingId === record.id) {
      article.append(createDeletePanel(record));
    }

    messageList.append(article);
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "请求失败，请稍后重试");
  }
  return data;
}

async function loadMessages() {
  setFeedback("正在加载聊天记录……");
  try {
    messages = await requestJson("/api/messages");
    renderMessages();
    setFeedback();
  } catch (error) {
    renderMessages();
    setFeedback(error.message, "error");
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    setFeedback("请先输入消息。", "error");
    return;
  }

  submitButton.disabled = true;
  setFeedback("正在发送……");
  try {
    const record = await requestJson("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messages.push(record);
    messageInput.value = "";
    renderMessages();
    setFeedback("消息已发送。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    submitButton.disabled = false;
    messageInput.focus();
  }
});

messageList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const id = Number(button.dataset.id);
  const action = button.dataset.action;

  if (action === "edit") {
    editingId = id;
    deletingId = null;
  } else if (action === "cancel-edit") {
    editingId = null;
  } else if (action === "delete") {
    deletingId = id;
    editingId = null;
  } else if (action === "cancel-delete") {
    deletingId = null;
  } else if (action === "confirm-delete") {
    button.disabled = true;
    setFeedback("正在删除……");
    try {
      await requestJson(`/api/messages/${id}`, { method: "DELETE" });
      messages = messages.filter((record) => record.id !== id);
      deletingId = null;
      setFeedback("聊天记录已删除。", "success");
    } catch (error) {
      setFeedback(error.message, "error");
    }
  }

  renderMessages();
});

messageList.addEventListener("submit", async (event) => {
  const form = event.target.closest(".edit-panel");
  if (!form) return;
  event.preventDefault();

  const id = Number(form.dataset.id);
  const message = new FormData(form).get("message").trim();
  if (!message) {
    setFeedback("修改后的消息不能为空。", "error");
    return;
  }

  const saveButton = form.querySelector("button[type='submit']");
  saveButton.disabled = true;
  setFeedback("正在保存……");
  try {
    const updated = await requestJson(`/api/messages/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messages = messages.map((record) => (record.id === id ? updated : record));
    editingId = null;
    renderMessages();
    setFeedback("聊天记录已修改。", "success");
  } catch (error) {
    saveButton.disabled = false;
    setFeedback(error.message, "error");
  }
});

loadMessages();

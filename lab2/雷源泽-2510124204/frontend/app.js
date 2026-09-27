"use strict";

const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const messageList = document.querySelector("#message-list");
const messageCount = document.querySelector("#message-count");
const feedback = document.querySelector("#feedback");
const connectionStatus = document.querySelector("#connection-status");

let messages = [];
let editingId = null;
let confirmingDeleteId = null;

function setFeedback(message = "", tone = "") {
  feedback.textContent = message;

  if (tone) {
    feedback.dataset.tone = tone;
  } else {
    delete feedback.dataset.tone;
  }
}

function setConnectionState(state, label) {
  connectionStatus.dataset.state = state;
  connectionStatus.textContent = label;
}

async function readResponse(response) {
  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message = payload?.error || `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }

  return payload;
}

function createElement(tagName, className, textContent) {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  if (textContent !== undefined) {
    element.textContent = textContent;
  }

  return element;
}

function createAuthorElement(author, isAssistant = false) {
  const className = isAssistant
    ? "message-author message-author--assistant"
    : "message-author";
  return createElement("span", className, author);
}

function renderMessage(record) {
  const card = createElement("article", "message-card");
  card.dataset.messageId = String(record.id);

  const userRow = createElement("div", "message-row");
  userRow.append(createAuthorElement("你"));

  if (editingId === record.id) {
    userRow.classList.add("message-row--editing");

    const form = createElement("form", "edit-form");
    const input = createElement("textarea", "edit-input");
    input.name = "message";
    input.maxLength = 2000;
    input.required = true;
    input.value = record.message;

    const actions = createElement("div", "edit-actions");
    const cancelButton = createElement("button", "secondary-button", "取消");
    cancelButton.type = "button";
    cancelButton.dataset.action = "cancel-edit";

    const saveButton = createElement("button", "save-button", "保存");
    saveButton.type = "submit";

    actions.append(cancelButton, saveButton);
    form.append(input, actions);
    userRow.append(form);
  } else if (confirmingDeleteId === record.id) {
    userRow.classList.add("message-row--editing");

    const confirmation = createElement("div", "delete-confirmation");
    confirmation.append(
      createElement("span", "confirmation-text", "确定删除这条记录？"),
    );

    const cancelButton = createElement("button", "secondary-button", "取消");
    cancelButton.type = "button";
    cancelButton.dataset.action = "cancel-delete";

    const deleteButton = createElement(
      "button",
      "danger-button",
      "确认删除",
    );
    deleteButton.type = "button";
    deleteButton.dataset.action = "confirm-delete";

    confirmation.append(cancelButton, deleteButton);
    userRow.append(confirmation);
  } else {
    userRow.append(createElement("p", "message-text", record.message));

    const actions = createElement("div", "message-actions");
    const editButton = createElement("button", "text-button", "修改");
    editButton.type = "button";
    editButton.dataset.action = "edit";

    const deleteButton = createElement(
      "button",
      "text-button text-button--danger",
      "删除",
    );
    deleteButton.type = "button";
    deleteButton.dataset.action = "delete";

    actions.append(editButton, deleteButton);
    userRow.append(actions);
  }

  const replyRow = createElement(
    "div",
    "message-row message-row--reply",
  );
  replyRow.append(
    createAuthorElement("AI", true),
    createElement("p", "message-text", record.reply),
  );

  card.append(userRow, replyRow);
  messageList.append(card);
}

function renderMessages() {
  messageList.replaceChildren();
  messageCount.textContent = `${messages.length} 条记录`;

  if (messages.length === 0) {
    const emptyState = createElement(
      "p",
      "empty-state",
      "还没有聊天记录，发送一条消息开始对话。",
    );
    messageList.append(emptyState);
    return;
  }

  messages.forEach(renderMessage);
}

async function loadMessages() {
  messageList.setAttribute("aria-busy", "true");

  try {
    const response = await fetch("/api/messages");
    const payload = await readResponse(response);

    if (!Array.isArray(payload)) {
      throw new Error("消息接口返回了无效的数据格式");
    }

    messages = payload;
    editingId = null;
    confirmingDeleteId = null;
    renderMessages();
    setConnectionState("online", "服务已连接");
    setFeedback();
  } catch (error) {
    setConnectionState("offline", "服务不可用");
    setFeedback(error.message, "error");
  } finally {
    messageList.setAttribute("aria-busy", "false");
  }
}

async function createMessage(event) {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) {
    setFeedback("请输入消息内容。", "error");
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  setFeedback("正在发送...");

  try {
    const response = await fetch("/api/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
    const record = await readResponse(response);

    messages.push(record);
    messageInput.value = "";
    renderMessages();
    setFeedback("消息已发送。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

async function updateMessage(messageId, message) {
  try {
    const response = await fetch(`/api/messages/${messageId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
    const updatedRecord = await readResponse(response);

    messages = messages.map((record) =>
      record.id === messageId ? updatedRecord : record,
    );
    editingId = null;
    renderMessages();
    setFeedback("消息已更新。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

async function deleteMessage(messageId) {
  try {
    const response = await fetch(`/api/messages/${messageId}`, {
      method: "DELETE",
    });
    await readResponse(response);

    messages = messages.filter((record) => record.id !== messageId);
    confirmingDeleteId = null;
    renderMessages();
    setFeedback("消息已删除。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

messageForm.addEventListener("submit", createMessage);

messageList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  const card = button.closest(".message-card");
  const messageId = Number(card.dataset.messageId);

  if (button.dataset.action === "edit") {
    editingId = messageId;
    confirmingDeleteId = null;
    renderMessages();
  } else if (button.dataset.action === "cancel-edit") {
    editingId = null;
    renderMessages();
  } else if (button.dataset.action === "delete") {
    confirmingDeleteId = messageId;
    editingId = null;
    renderMessages();
  } else if (button.dataset.action === "cancel-delete") {
    confirmingDeleteId = null;
    renderMessages();
  } else if (button.dataset.action === "confirm-delete") {
    void deleteMessage(messageId);
  }
});

messageList.addEventListener("submit", (event) => {
  if (!event.target.matches(".edit-form")) {
    return;
  }

  event.preventDefault();
  const card = event.target.closest(".message-card");
  const messageId = Number(card.dataset.messageId);
  const message = event.target.querySelector(".edit-input").value.trim();

  if (!message) {
    setFeedback("消息内容不能为空。", "error");
    return;
  }

  void updateMessage(messageId, message);
});

void loadMessages();

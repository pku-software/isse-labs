const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const feedback = document.querySelector("#feedback");
const sendButton = messageForm.querySelector("button[type='submit']");

let messages = [];
let editingId = null;
let deletingId = null;

function setFeedback(text = "", type = "error") {
  feedback.textContent = text;
  feedback.classList.toggle("success", type === "success");
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = response.status === 204 ? null : await response.json();

  if (!response.ok) {
    throw new Error(data?.error || "请求失败，请稍后重试");
  }

  return data;
}

function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
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

  messages.forEach((item) => {
    const card = document.createElement("article");
    card.className = "message-card";

    if (editingId === item.id) {
      renderEditPanel(card, item);
    } else if (deletingId === item.id) {
      renderDeletePanel(card, item);
    } else {
      renderMessageCard(card, item);
    }

    messageList.append(card);
  });
}

function renderMessageCard(card, item) {
  const content = document.createElement("div");
  content.className = "message-content";

  const userRole = document.createElement("p");
  userRole.className = "message-role";
  userRole.textContent = "你";
  const userMessage = document.createElement("p");
  userMessage.textContent = item.message;
  const assistantRole = document.createElement("p");
  assistantRole.className = "message-role assistant";
  assistantRole.textContent = "AI";
  const assistantReply = document.createElement("p");
  assistantReply.textContent = item.reply;
  content.append(userRole, userMessage, assistantRole, assistantReply);

  const actions = document.createElement("div");
  actions.className = "message-actions";
  actions.append(
    createButton("修改", "text-button", () => {
      editingId = item.id;
      deletingId = null;
      setFeedback();
      renderMessages();
    }),
    createButton("删除", "text-button danger", () => {
      deletingId = item.id;
      editingId = null;
      setFeedback();
      renderMessages();
    }),
  );

  card.append(content, actions);
}

function renderEditPanel(card, item) {
  const panel = document.createElement("form");
  panel.className = "edit-panel";

  const label = document.createElement("label");
  label.textContent = "修改消息";
  const input = document.createElement("textarea");
  input.value = item.message;
  input.required = true;
  label.append(input);

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createButton("取消", "secondary-button", () => {
      editingId = null;
      renderMessages();
    }),
  );
  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.className = "send-button";
  saveButton.textContent = "保存";
  actions.append(saveButton);

  panel.addEventListener("submit", async (event) => {
    event.preventDefault();
    saveButton.disabled = true;
    try {
      const updated = await requestJson(`/api/messages/${item.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input.value }),
      });
      messages = messages.map((message) =>
        message.id === updated.id ? updated : message,
      );
      editingId = null;
      setFeedback("聊天记录已修改。", "success");
      renderMessages();
    } catch (error) {
      setFeedback(error.message);
      saveButton.disabled = false;
    }
  });

  panel.append(label, actions);
  card.append(panel);
  input.focus();
}

function renderDeletePanel(card, item) {
  const panel = document.createElement("div");
  panel.className = "delete-panel";
  const question = document.createElement("p");
  question.textContent = `确定删除“${item.message}”吗？`;

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  const cancelButton = createButton("取消", "secondary-button", () => {
    deletingId = null;
    renderMessages();
  });
  const deleteButton = createButton("确认删除", "danger-button", async () => {
    deleteButton.disabled = true;
    try {
      await requestJson(`/api/messages/${item.id}`, { method: "DELETE" });
      messages = messages.filter((message) => message.id !== item.id);
      deletingId = null;
      setFeedback("聊天记录已删除。", "success");
      renderMessages();
    } catch (error) {
      setFeedback(error.message);
      deleteButton.disabled = false;
    }
  });
  actions.append(cancelButton, deleteButton);
  panel.append(question, actions);
  card.append(panel);
}

async function loadMessages() {
  try {
    messages = await requestJson("/api/messages");
    renderMessages();
  } catch (error) {
    setFeedback(error.message);
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  sendButton.disabled = true;
  setFeedback();

  try {
    const created = await requestJson("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: messageInput.value }),
    });
    messages.push(created);
    messageInput.value = "";
    setFeedback("消息已发送。", "success");
    renderMessages();
  } catch (error) {
    setFeedback(error.message);
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
});

loadMessages();

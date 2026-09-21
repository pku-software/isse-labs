const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const feedback = document.querySelector("#page-feedback");

let messages = [];
let editingId = null;
let deletingId = null;

function showFeedback(text = "", type = "") {
  feedback.textContent = text;
  feedback.className = `page-feedback ${type}`.trim();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）`);
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

function createMessageRow(role, text, className) {
  const row = document.createElement("div");
  row.className = `message-row ${className}`;

  const roleLabel = document.createElement("span");
  roleLabel.className = "role-label";
  roleLabel.textContent = role;

  const content = document.createElement("p");
  content.textContent = text;

  row.append(roleLabel, content);
  return row;
}

function renderEditPanel(message, card) {
  const panel = document.createElement("div");
  panel.className = "edit-panel";

  const input = document.createElement("input");
  input.className = "edit-input";
  input.type = "text";
  input.value = message.message;
  input.setAttribute("aria-label", "修改消息内容");

  const saveButton = createButton("保存", "action-button", async () => {
    const newText = input.value.trim();
    if (!newText) {
      showFeedback("修改内容不能为空。", "error");
      input.focus();
      return;
    }

    saveButton.disabled = true;
    try {
      const updated = await apiRequest(`/api/messages/${message.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newText }),
      });
      messages = messages.map((item) => (item.id === updated.id ? updated : item));
      editingId = null;
      showFeedback("聊天记录已修改。", "success");
      renderMessages();
    } catch (error) {
      showFeedback(error.message, "error");
      saveButton.disabled = false;
    }
  });

  const cancelButton = createButton("取消", "action-button secondary", () => {
    editingId = null;
    showFeedback();
    renderMessages();
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveButton.click();
    }
  });

  panel.append(input, saveButton, cancelButton);
  card.append(panel);
  window.requestAnimationFrame(() => input.focus());
}

function renderDeletePanel(message, card) {
  const panel = document.createElement("div");
  panel.className = "delete-panel";

  const prompt = document.createElement("p");
  prompt.textContent = "确定删除这条聊天记录吗？";

  const confirmButton = createButton("确认删除", "action-button danger", async () => {
    confirmButton.disabled = true;
    try {
      await apiRequest(`/api/messages/${message.id}`, { method: "DELETE" });
      messages = messages.filter((item) => item.id !== message.id);
      deletingId = null;
      showFeedback("聊天记录已删除。", "success");
      renderMessages();
    } catch (error) {
      showFeedback(error.message, "error");
      confirmButton.disabled = false;
    }
  });

  const cancelButton = createButton("取消", "action-button secondary", () => {
    deletingId = null;
    showFeedback();
    renderMessages();
  });

  panel.append(prompt, confirmButton, cancelButton);
  card.append(panel);
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

  for (const message of messages) {
    const card = document.createElement("article");
    card.className = "message-card";
    card.append(
      createMessageRow("你", message.message, "user-message"),
      createMessageRow("AI", message.reply, "assistant-message"),
    );

    const actions = document.createElement("div");
    actions.className = "message-actions";
    actions.setAttribute("aria-label", "聊天记录操作");
    actions.append(
      createButton("修改", "text-button", () => {
        editingId = message.id;
        deletingId = null;
        showFeedback();
        renderMessages();
      }),
      createButton("删除", "text-button danger", () => {
        deletingId = message.id;
        editingId = null;
        showFeedback();
        renderMessages();
      }),
    );
    card.append(actions);

    if (editingId === message.id) {
      renderEditPanel(message, card);
    } else if (deletingId === message.id) {
      renderDeletePanel(message, card);
    }

    messageList.append(card);
  }
}

async function loadMessages() {
  try {
    messages = await apiRequest("/api/messages");
    renderMessages();
  } catch (error) {
    messageList.replaceChildren();
    showFeedback(error.message, "error");
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();

  if (!text) {
    showFeedback("请先输入消息。", "error");
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  showFeedback("正在发送……");
  try {
    const created = await apiRequest("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    messages.push(created);
    messageInput.value = "";
    showFeedback("消息已发送。", "success");
    renderMessages();
    messageInput.focus();
  } catch (error) {
    showFeedback(error.message, "error");
  } finally {
    sendButton.disabled = false;
  }
});

loadMessages();

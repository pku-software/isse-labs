const chatPanel = document.querySelector("#chat-panel");
const composer = document.querySelector(".composer");
const messageInput = document.querySelector("#message-input");
const feedback = document.querySelector("#page-feedback");

let messages = [];
let editingId = null;
let pendingDeleteId = null;

function setFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.classList.toggle("is-error", isError);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）`);
  }

  return data;
}

function createMessageBlock(role, text, isAssistant = false) {
  const block = document.createElement("div");
  block.className = `message-block${isAssistant ? " assistant-message" : ""}`;

  const roleLabel = document.createElement("span");
  roleLabel.className = "message-role";
  roleLabel.textContent = role;

  const content = document.createElement("p");
  content.textContent = text;

  block.append(roleLabel, content);
  return block;
}

function renderMessages() {
  chatPanel.replaceChildren();

  if (messages.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "还没有聊天记录，发送一条消息开始吧。";
    chatPanel.append(emptyState);
    return;
  }

  messages.forEach((record) => {
    const card = document.createElement("article");
    card.className = "message-card";

    if (editingId === record.id) {
      const editor = document.createElement("div");
      editor.className = "inline-editor";

      const label = document.createElement("label");
      label.htmlFor = `edit-message-${record.id}`;
      label.textContent = "修改你的消息";

      const textarea = document.createElement("textarea");
      textarea.id = `edit-message-${record.id}`;
      textarea.value = record.message;
      textarea.rows = 3;

      const actions = document.createElement("div");
      actions.className = "record-actions";
      actions.append(
        makeButton("取消", "button-secondary", () => {
          editingId = null;
          renderMessages();
        }),
        makeButton("保存", "button-primary", () => updateMessage(record.id, textarea.value)),
      );

      editor.append(label, textarea, actions);
      card.append(editor);
    } else {
      card.append(
        createMessageBlock("你", record.message),
        createMessageBlock("AI", record.reply, true),
      );

      const actions = document.createElement("div");
      actions.className = "record-actions";
      actions.setAttribute("aria-label", "记录操作");
      actions.append(
        makeButton("修改", "button-secondary", () => {
          editingId = record.id;
          pendingDeleteId = null;
          renderMessages();
        }),
        makeButton("删除", "button-danger", () => {
          pendingDeleteId = record.id;
          editingId = null;
          renderMessages();
        }),
      );
      card.append(actions);
    }

    if (pendingDeleteId === record.id) {
      const confirmation = document.createElement("div");
      confirmation.className = "delete-confirmation";

      const question = document.createElement("p");
      question.textContent = "确定删除这条聊天记录吗？";

      const actions = document.createElement("div");
      actions.className = "record-actions";
      actions.append(
        makeButton("取消", "button-secondary", () => {
          pendingDeleteId = null;
          renderMessages();
        }),
        makeButton("确认删除", "button-danger", () => deleteMessage(record.id)),
      );

      confirmation.append(question, actions);
      card.append(confirmation);
    }

    chatPanel.append(card);
  });
}

function makeButton(label, styleClass, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${styleClass}`;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

async function loadMessages() {
  try {
    messages = await apiRequest("/api/messages");
    renderMessages();
  } catch (error) {
    setFeedback(error.message, true);
    chatPanel.innerHTML = '<p class="empty-state">无法加载聊天记录。</p>';
  }
}

async function updateMessage(id, message) {
  try {
    const updated = await apiRequest(`/api/messages/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messages = messages.map((item) => (item.id === id ? updated : item));
    editingId = null;
    renderMessages();
    setFeedback("聊天记录已修改。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

async function deleteMessage(id) {
  try {
    await apiRequest(`/api/messages/${id}`, { method: "DELETE" });
    messages = messages.filter((item) => item.id !== id);
    pendingDeleteId = null;
    renderMessages();
    setFeedback("聊天记录已删除。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) {
    setFeedback("请先输入消息。", true);
    messageInput.focus();
    return;
  }

  const submitButton = composer.querySelector('[type="submit"]');
  submitButton.disabled = true;
  setFeedback("正在发送……");

  try {
    const created = await apiRequest("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messages.push(created);
    messageInput.value = "";
    renderMessages();
    setFeedback("消息已发送。");
  } catch (error) {
    setFeedback(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

loadMessages();

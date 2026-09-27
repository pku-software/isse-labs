const messageList = document.querySelector("#message-list");
const recordCount = document.querySelector("#record-count");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const formStatus = document.querySelector("#form-status");

let messages = [];

function setStatus(text, type = "info") {
  formStatus.textContent = text;
  formStatus.classList.toggle("is-error", type === "error");
  formStatus.classList.toggle("is-success", type === "success");
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "请求失败，请稍后重试");
  }

  return data;
}

function createButton(text, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${className}`;
  button.textContent = text;
  button.addEventListener("click", onClick);
  return button;
}

function createMessageLine(label, text, isAssistant = false) {
  const line = document.createElement("div");
  line.className = `message-line${isAssistant ? " reply-line" : ""}`;

  const labelElement = document.createElement("span");
  labelElement.className = `message-label${isAssistant ? " assistant-label" : ""}`;
  labelElement.textContent = label;

  const textElement = document.createElement("p");
  textElement.textContent = text;

  line.append(labelElement, textElement);
  return line;
}

function showEditor(card, record) {
  card.querySelector(".message-editor")?.remove();
  card.querySelector(".delete-confirmation")?.remove();

  const editor = document.createElement("div");
  editor.className = "message-editor";

  const textarea = document.createElement("textarea");
  textarea.value = record.message;
  textarea.setAttribute("aria-label", "修改消息内容");

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createButton("取消", "button-secondary", () => editor.remove()),
    createButton("保存修改", "button-primary", async () => {
      const newMessage = textarea.value.trim();
      if (!newMessage) {
        setStatus("修改内容不能为空。", "error");
        textarea.focus();
        return;
      }

      try {
        const updated = await requestJson(`/api/messages/${record.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: newMessage }),
        });
        messages = messages.map((item) => (item.id === updated.id ? updated : item));
        renderMessages();
        setStatus("聊天记录已修改。", "success");
      } catch (error) {
        setStatus(error.message, "error");
      }
    }),
  );

  editor.append(textarea, actions);
  card.append(editor);
  textarea.focus();
}

function showDeleteConfirmation(card, record) {
  card.querySelector(".message-editor")?.remove();
  card.querySelector(".delete-confirmation")?.remove();

  const confirmation = document.createElement("div");
  confirmation.className = "delete-confirmation";

  const text = document.createElement("p");
  text.textContent = "确定删除这条聊天记录吗？";

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createButton("取消", "button-secondary", () => confirmation.remove()),
    createButton("确认删除", "button-danger", async () => {
      try {
        await requestJson(`/api/messages/${record.id}`, { method: "DELETE" });
        messages = messages.filter((item) => item.id !== record.id);
        renderMessages();
        setStatus("聊天记录已删除。", "success");
      } catch (error) {
        setStatus(error.message, "error");
      }
    }),
  );

  confirmation.append(text, actions);
  card.append(confirmation);
}

function createMessageCard(record) {
  const card = document.createElement("article");
  card.className = "message-card";

  const content = document.createElement("div");
  content.className = "message-content";
  content.append(
    createMessageLine("你", record.message),
    createMessageLine("AI", record.reply, true),
  );

  const actions = document.createElement("div");
  actions.className = "message-actions";
  actions.setAttribute("aria-label", "聊天记录操作");
  actions.append(
    createButton("修改", "button-secondary", () => showEditor(card, record)),
    createButton("删除", "button-danger", () => showDeleteConfirmation(card, record)),
  );

  card.append(content, actions);
  return card;
}

function renderMessages() {
  messageList.replaceChildren();
  recordCount.textContent = `${messages.length} 条记录`;

  if (messages.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "还没有聊天记录，发送第一条消息吧。";
    messageList.append(emptyState);
    return;
  }

  messages.forEach((record) => messageList.append(createMessageCard(record)));
}

async function loadMessages() {
  try {
    messages = await requestJson("/api/messages");
    renderMessages();
    setStatus("聊天记录已加载。", "success");
  } catch (error) {
    messageList.replaceChildren();
    const errorState = document.createElement("p");
    errorState.className = "empty-state";
    errorState.textContent = "聊天记录加载失败。";
    messageList.append(errorState);
    setStatus(error.message, "error");
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();

  if (!message) {
    setStatus("请输入消息内容。", "error");
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  setStatus("正在发送……");

  try {
    const created = await requestJson("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messages.push(created);
    renderMessages();
    messageForm.reset();
    setStatus("消息已发送，后端已返回回复。", "success");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    sendButton.disabled = false;
  }
});

loadMessages();

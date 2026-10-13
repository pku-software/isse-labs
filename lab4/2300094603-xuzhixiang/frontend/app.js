const messageList = document.querySelector("#message-list");
const composer = document.querySelector("#composer");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const statusMessage = document.querySelector("#status-message");
const recordCount = document.querySelector("#record-count");

function showStatus(message = "", kind = "") {
  statusMessage.textContent = message;
  statusMessage.className = `status-message ${kind}`;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）`);
  }
  return data;
}

function makeTextBlock(label, text, extraClass = "") {
  const group = document.createElement("div");
  const heading = document.createElement("p");
  heading.className = `message-label ${extraClass}`;
  heading.textContent = label;
  const content = document.createElement("p");
  content.className = "message-text";
  content.textContent = text;
  group.append(heading, content);
  return group;
}

function renderMessages(messages) {
  messageList.replaceChildren();
  recordCount.textContent = `${messages.length} 条记录`;

  if (messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const icon = document.createElement("div");
    icon.className = "empty-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = "✳";
    const title = document.createElement("h3");
    title.textContent = "从一个问题开始";
    const description = document.createElement("p");
    description.textContent = "发送消息后，聊天记录会显示在这里。";
    empty.append(icon, title, description);
    messageList.append(empty);
    return;
  }

  for (const message of messages) {
    const card = document.createElement("article");
    card.className = "message-card";
    card.dataset.id = message.id;

    const copy = document.createElement("div");
    copy.className = "message-copy";
    copy.append(makeTextBlock("你", message.message));
    copy.append(makeTextBlock("AI 助手", message.reply, "assistant-label"));

    const actions = document.createElement("div");
    actions.className = "message-actions";
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "edit-button";
    editButton.textContent = "修改";
    editButton.addEventListener("click", () => beginEdit(card, message));
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.textContent = "删除";
    deleteButton.addEventListener("click", () => beginDelete(card, message.id));
    actions.append(editButton, deleteButton);

    card.append(copy, actions);
    messageList.append(card);
  }
}

async function loadMessages() {
  try {
    const data = await requestJson("/api/messages");
    renderMessages(data.messages);
  } catch (error) {
    recordCount.textContent = "加载失败";
    showStatus(error.message, "error");
  }
}

function beginEdit(card, message) {
  const editor = document.createElement("div");
  editor.className = "inline-editor";
  const textarea = document.createElement("textarea");
  textarea.rows = 2;
  textarea.value = message.message;
  textarea.setAttribute("aria-label", "修改聊天内容");
  const controls = document.createElement("div");
  controls.className = "inline-controls";
  const save = document.createElement("button");
  save.type = "button";
  save.className = "small-button primary-small";
  save.textContent = "保存修改";
  save.addEventListener("click", async () => {
    try {
      await requestJson(`/api/messages/${message.id}`, {
        method: "PATCH",
        body: JSON.stringify({ message: textarea.value }),
      });
      showStatus("聊天记录已修改。", "success");
      await loadMessages();
    } catch (error) {
      showStatus(error.message, "error");
    }
  });
  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "small-button";
  cancel.textContent = "取消";
  cancel.addEventListener("click", loadMessages);
  controls.append(save, cancel);
  editor.append(textarea, controls);
  card.querySelector(".message-copy").append(editor);
  card.querySelector(".message-actions").hidden = true;
  textarea.focus();
}

function beginDelete(card, messageId) {
  const confirmation = document.createElement("div");
  confirmation.className = "delete-confirmation";
  const prompt = document.createElement("span");
  prompt.textContent = "确定删除这条记录吗？";
  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "small-button danger-small";
  remove.textContent = "确认删除";
  remove.addEventListener("click", async () => {
    try {
      await requestJson(`/api/messages/${messageId}`, { method: "DELETE" });
      showStatus("聊天记录已删除。", "success");
      await loadMessages();
    } catch (error) {
      showStatus(error.message, "error");
    }
  });
  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "small-button";
  cancel.textContent = "取消";
  cancel.addEventListener("click", () => confirmation.remove());
  confirmation.append(prompt, remove, cancel);
  card.append(confirmation);
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    showStatus("请输入消息后再发送。", "error");
    return;
  }

  sendButton.disabled = true;
  showStatus("正在发送…");
  try {
    await requestJson("/api/messages", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    messageInput.value = "";
    showStatus("已收到回复。", "success");
    await loadMessages();
  } catch (error) {
    showStatus(error.message, "error");
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
});

loadMessages();

"use strict";

const apiUrl = "/api/messages";
const messageList = document.querySelector("#message-list");
const emptyState = document.querySelector("#empty-state");
const recordCount = document.querySelector(".record-count");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const statusMessage = document.querySelector("#status-message");


function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error-message", isError);
}


function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}


function createEditPanel(record, card) {
  const panel = document.createElement("div");
  panel.className = "edit-panel";

  const label = document.createElement("label");
  const inputId = `edit-message-${record.id}`;
  label.htmlFor = inputId;
  label.textContent = "修改你的问题";

  const input = document.createElement("textarea");
  input.id = inputId;
  input.rows = 3;
  input.value = record.message;

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  const saveButton = createButton("保存修改", "primary-button", async () => {
    const message = input.value.trim();
    if (!message) {
      setStatus("请输入要保存的消息。", true);
      input.focus();
      return;
    }

    saveButton.disabled = true;
    try {
      await requestJson(`${apiUrl}/${record.id}`, "PATCH", { message });
      setStatus("消息已修改。");
      await loadMessages();
    } catch (error) {
      setStatus(error.message, true);
    } finally {
      saveButton.disabled = false;
    }
  });
  const cancelButton = createButton("取消", "text-button", () => panel.remove());

  actions.append(saveButton, cancelButton);
  panel.append(label, input, actions);
  card.append(panel);
  input.focus();
}


function createDeletePanel(record, card) {
  const panel = document.createElement("div");
  panel.className = "delete-panel";

  const text = document.createElement("p");
  text.textContent = "确定删除这条聊天记录吗？此操作无法撤销。";
  const actions = document.createElement("div");
  actions.className = "inline-actions";
  const confirmButton = createButton("确认删除", "danger-button", async () => {
    confirmButton.disabled = true;
    try {
      await requestJson(`${apiUrl}/${record.id}`, "DELETE");
      setStatus("消息已删除。");
      await loadMessages();
    } catch (error) {
      setStatus(error.message, true);
    } finally {
      confirmButton.disabled = false;
    }
  });
  const cancelButton = createButton("取消", "text-button", () => panel.remove());

  actions.append(confirmButton, cancelButton);
  panel.append(text, actions);
  card.append(panel);
}


function createMessageCard(record) {
  const card = document.createElement("article");
  card.className = "message-card";

  const content = document.createElement("div");
  content.className = "message-content";
  const questionLabel = document.createElement("p");
  questionLabel.className = "message-label";
  questionLabel.textContent = "你的问题";
  const question = document.createElement("p");
  question.textContent = record.message;
  const replyLabel = document.createElement("p");
  replyLabel.className = "message-label reply-label";
  replyLabel.textContent = "AI 回复";
  const reply = document.createElement("p");
  reply.textContent = record.reply;
  content.append(questionLabel, question, replyLabel, reply);

  const actions = document.createElement("div");
  actions.className = "message-actions";
  actions.setAttribute("aria-label", "记录操作");
  actions.append(
    createButton("修改", "secondary-button", () => {
      card.querySelector(".delete-panel, .edit-panel")?.remove();
      createEditPanel(record, card);
    }),
    createButton("删除", "danger-button", () => {
      card.querySelector(".delete-panel, .edit-panel")?.remove();
      createDeletePanel(record, card);
    }),
  );

  card.append(content, actions);
  return card;
}


function renderMessages(records) {
  messageList.replaceChildren(...records.map(createMessageCard));
  emptyState.hidden = records.length > 0;
  recordCount.textContent = `${records.length} 条记录`;
}


async function requestJson(url, method = "GET", body) {
  const options = { method, headers: { Accept: "application/json" } };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败，请稍后重试。");
  }
  return data;
}


async function loadMessages() {
  try {
    const records = await requestJson(apiUrl);
    renderMessages(records);
    if (!records.length) {
      setStatus("还没有聊天记录，发送第一条消息吧。");
    }
  } catch (error) {
    setStatus(`无法加载聊天记录：${error.message}`, true);
  }
}


messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    setStatus("请输入消息后再发送。", true);
    messageInput.focus();
    return;
  }

  const submitButton = messageForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  try {
    await requestJson(apiUrl, "POST", { message });
    messageInput.value = "";
    setStatus("消息已发送，AI 已回复“你好”。");
    await loadMessages();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});


loadMessages();

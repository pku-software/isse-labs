"use strict";

const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const reloadButton = document.querySelector("#reload-button");
const recordCount = document.querySelector("#record-count");
const statusMessage = document.querySelector("#status-message");

let records = [];
let loaded = false;
let busy = false;
let editingId = null;
let deletingId = null;

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function showStatus(text, isError = false) {
  statusMessage.textContent = text;
  statusMessage.classList.toggle("is-error", isError);
  statusMessage.setAttribute("role", isError ? "alert" : "status");
}

function updateControls() {
  reloadButton.disabled = busy;
  messageInput.disabled = busy || !loaded;
  sendButton.disabled = busy || !loaded;
  messageList.setAttribute("aria-busy", String(busy));
  messageList.querySelectorAll("button, textarea").forEach((control) => {
    control.disabled = busy;
  });
}

// 所有数据读写通过自己的 Flask API 完成；用户文字只作为文本显示。
async function api(path, method = "GET", data) {
  const options = { method, headers: { Accept: "application/json" }, cache: "no-store" };
  if (data !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }

  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("无法连接服务。请确认服务已启动，并通过 http://localhost:5001/ 访问页面。");
  }
  if (response.status === 204) return null;

  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`服务返回了无法识别的响应（HTTP ${response.status}）。`);
  }
  if (!response.ok) {
    throw new Error(result.error || `请求失败（HTTP ${response.status}）。`);
  }
  return result;
}

async function runAction(action, successText) {
  if (busy) return false;
  busy = true;
  updateControls();
  showStatus("正在处理…");
  try {
    await action();
    renderRecords();
    showStatus(successText);
    return true;
  } catch (error) {
    showStatus(error.message, true);
    return false;
  } finally {
    busy = false;
    updateControls();
  }
}

function actionButton(label, handler, extraClass = "") {
  const button = element("button", `text-button ${extraClass}`, label);
  button.type = "button";
  button.addEventListener("click", handler);
  return button;
}

function messageRow(role, text) {
  const isUser = role === "user";
  const row = element("div", `message-row ${role}-row`);
  const avatar = element("span", `avatar ${role}-avatar`, isUser ? "你" : "AI");
  avatar.setAttribute("aria-hidden", "true");
  const content = element("div", "message-content");
  content.append(
    element("span", "speaker", isUser ? "你的问题" : "AI 助手"),
    element("p", `bubble ${role}-bubble`, text),
  );
  row.append(avatar, content);
  return row;
}

function closeRecordAction() {
  const previousId = editingId ?? deletingId;
  editingId = null;
  deletingId = null;
  renderRecords();
  messageList.querySelector(`[data-record-id="${previousId}"] button`)?.focus();
}

function editForm(record) {
  const form = element("form", "edit-form");
  form.noValidate = true;
  const label = element("label", "edit-label", "修改问题");
  const input = element("textarea", "edit-input");
  input.id = `edit-message-${record.id}`;
  input.value = record.message;
  input.rows = 3;
  input.maxLength = 4000;
  input.required = true;
  label.htmlFor = input.id;
  const errorText = element("p", "inline-error");
  errorText.id = `edit-error-${record.id}`;
  errorText.setAttribute("role", "alert");
  input.setAttribute("aria-describedby", errorText.id);

  const controls = element("div", "inline-actions");
  const saveButton = element("button", "send-button", "保存修改");
  saveButton.type = "submit";
  controls.append(saveButton, actionButton("取消", closeRecordAction));
  form.append(label, input, errorText, controls);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    const message = input.value.trim();
    if (!message) {
      errorText.textContent = "问题不能只包含空格。";
      input.focus();
      return;
    }
    errorText.textContent = "";
    const saved = await runAction(async () => {
      const updated = await api(`/api/messages/${record.id}`, "PATCH", { message });
      records = records.map((item) => item.id === updated.id ? updated : item);
      editingId = null;
    }, "聊天记录已修改。");
    if (saved) messageList.querySelector(`[data-record-id="${record.id}"] button`)?.focus();
  });
  return form;
}

function deleteConfirmation(record) {
  const box = element("div", "delete-confirmation");
  box.append(element("p", "", "确定删除这条问题及其回答？删除后无法恢复。"));
  const controls = element("div", "inline-actions");
  controls.append(
    actionButton("确认删除", async () => {
      const deleted = await runAction(async () => {
        await api(`/api/messages/${record.id}`, "DELETE");
        records = records.filter((item) => item.id !== record.id);
        deletingId = null;
      }, "聊天记录已删除。");
      if (deleted) messageInput.focus();
    }, "danger-button"),
    actionButton("取消", closeRecordAction),
  );
  box.append(controls);
  return box;
}

function renderRecord(record) {
  const article = element("article", "message-record");
  article.dataset.recordId = record.id;
  article.setAttribute("aria-label", `聊天记录 ${record.id}`);
  article.append(messageRow("user", record.message), messageRow("assistant", record.reply));

  if (editingId === record.id) {
    article.append(editForm(record));
  } else if (deletingId === record.id) {
    article.append(deleteConfirmation(record));
  } else {
    const actions = element("div", "record-actions");
    actions.append(
      actionButton("修改", () => {
        editingId = record.id;
        deletingId = null;
        renderRecords();
        document.querySelector(`#edit-message-${record.id}`).focus();
      }),
      actionButton("删除", () => {
        deletingId = record.id;
        editingId = null;
        renderRecords();
        messageList.querySelector(".delete-confirmation button").focus();
      }, "delete-button"),
    );
    article.append(actions);
  }
  return article;
}

function renderRecords() {
  recordCount.textContent = `${records.length} 条记录`;
  if (records.length === 0) {
    messageList.replaceChildren(element("p", "empty-state", "还没有聊天记录，写下你的第一个问题吧。"));
  } else {
    messageList.replaceChildren(...records.map(renderRecord));
  }
  updateControls();
}

async function loadRecords() {
  const success = await runAction(async () => {
    const result = await api("/api/messages");
    if (!Array.isArray(result)) throw new Error("聊天列表格式不正确，请检查服务后重试。");
    records = result;
    loaded = true;
    editingId = null;
    deletingId = null;
  }, "聊天记录已加载。");
  if (!success && !loaded) {
    messageList.replaceChildren(element("p", "empty-state", "暂时无法加载记录，请点击“刷新列表”重试。"));
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy || !loaded) return;
  const message = messageInput.value.trim();
  if (!message) {
    showStatus("请先输入问题，内容不能只包含空格。", true);
    messageInput.focus();
    return;
  }
  const sent = await runAction(async () => {
    const record = await api("/api/messages", "POST", { message });
    records.push(record);
    editingId = null;
    deletingId = null;
    messageInput.value = "";
  }, "消息已发送，回复已收到。");
  if (sent) {
    messageList.scrollTop = messageList.scrollHeight;
    messageInput.focus();
  }
});

reloadButton.addEventListener("click", loadRecords);
loadRecords();

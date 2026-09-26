"use strict";

const page = document.querySelector(".chat-app");
const list = document.querySelector("#message-list");
const form = document.querySelector("#message-form");
const input = document.querySelector("#message-input");
const status = document.querySelector("#status-message");
const reloadButton = document.querySelector("#reload-button");
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

function showStatus(message, isError = false) {
  status.textContent = message;
  status.classList.toggle("is-error", isError);
}

function setBusy(value) {
  busy = value;
  list.setAttribute("aria-busy", String(value));
  page.querySelectorAll("button, textarea").forEach((control) => {
    control.disabled = value || (!loaded && control.id !== "reload-button");
  });
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("无法连接服务。请确认 Flask 正在运行，再重试。");
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`服务返回了无法解析的内容（HTTP ${response.status}）。`);
  }
  if (!response.ok) {
    throw new Error(data.error || `请求失败（HTTP ${response.status}）。`);
  }
  return data;
}

function jsonOptions(method, message) {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  };
}

// 同一时刻只发送一个操作，避免重复点击以及界面更新顺序混乱。
async function performAction(action, pendingMessage) {
  if (busy) return;
  setBusy(true);
  showStatus(pendingMessage);
  try {
    await action();
  } catch (error) {
    showStatus(error.message, true);
  } finally {
    setBusy(false);
  }
}

function button(text, className, onClick) {
  const node = element("button", className, text);
  node.type = "button";
  node.addEventListener("click", onClick);
  return node;
}

function focusAction(id, action) {
  document.getElementById(`${action}-${id}`)?.focus();
}

function editPanel(record) {
  const panel = element("form", "inline-panel");
  const label = element("label", "", "修改你的提问");
  label.htmlFor = `edit-input-${record.id}`;
  const editor = element("textarea", "");
  editor.id = label.htmlFor;
  editor.value = record.message;
  editor.rows = 3;
  editor.required = true;
  const note = element("p", "panel-note", "保存后更新提问，保留这条问答的现有回复。");
  note.id = `edit-note-${record.id}`;
  editor.setAttribute("aria-describedby", note.id);
  const actions = element("div", "panel-actions");
  const save = element("button", "send-button", "保存提问");
  save.type = "submit";
  const cancel = button("取消", "text-button", () => {
    editingId = null;
    renderRecords();
    focusAction(record.id, "edit");
  });
  actions.append(save, cancel);
  panel.append(label, editor, note, actions);
  panel.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = editor.value.trim();
    if (!message) {
      showStatus("提问不能为空，请输入文字。", true);
      editor.focus();
      return;
    }
    performAction(async () => {
      const updated = await api(`/api/messages/${record.id}`, jsonOptions("PATCH", message));
      records = records.map((item) => item.id === updated.id ? updated : item);
      editingId = null;
      renderRecords();
      showStatus("提问已更新。");
      // 新生成的控件在请求结束时统一恢复可用。
    }, "正在保存提问……").then(() => {
      if (editingId === null) focusAction(record.id, "edit");
      else editor.focus();
    });
  });
  return panel;
}

function deletePanel(record) {
  const panel = element("div", "inline-panel delete-panel");
  const note = element("p", "panel-note", "删除这整条问答？提问和回复都会被删除，此操作无法撤销。");
  const actions = element("div", "panel-actions");
  const cancel = button("取消", "text-button", () => {
    deletingId = null;
    renderRecords();
    focusAction(record.id, "delete");
  });
  cancel.id = `cancel-delete-${record.id}`;
  const confirm = button("确认删除", "text-button delete-button", () => {
    performAction(async () => {
      await api(`/api/messages/${record.id}`, { method: "DELETE" });
      records = records.filter((item) => item.id !== record.id);
      deletingId = null;
      renderRecords();
      showStatus("整条问答已删除。");
    }, "正在删除问答……").then(() => {
      if (deletingId === null) input.focus();
      else cancel.focus();
    });
  });
  actions.append(cancel, confirm);
  panel.append(note, actions);
  return panel;
}

function renderRecords() {
  list.replaceChildren();
  if (records.length === 0) {
    list.append(element("p", "empty-state", "还没有问答。在下方写下你的第一个问题吧。"));
  }
  for (const record of records) {
    const article = element("article", "message-record");
    article.setAttribute("aria-label", `问答 ${record.id}`);
    const question = element("div", "question");
    question.append(element("p", "speaker", "你"), element("p", "message-text", record.message));
    const answer = element("div", "answer");
    answer.append(element("p", "speaker", "AI 助手"), element("p", "message-text", record.reply));
    const actions = element("div", "record-actions");
    actions.setAttribute("aria-label", "整条问答的操作");
    const edit = button("修改提问", "text-button", () => {
      editingId = record.id;
      deletingId = null;
      renderRecords();
      document.getElementById(`edit-input-${record.id}`).focus();
    });
    edit.id = `edit-${record.id}`;
    edit.setAttribute("aria-expanded", String(editingId === record.id));
    const remove = button("删除问答", "text-button delete-button", () => {
      deletingId = record.id;
      editingId = null;
      renderRecords();
      document.getElementById(`cancel-delete-${record.id}`).focus();
    });
    remove.id = `delete-${record.id}`;
    remove.setAttribute("aria-expanded", String(deletingId === record.id));
    actions.append(edit, remove);
    article.append(question, answer, actions);
    if (editingId === record.id) article.append(editPanel(record));
    if (deletingId === record.id) article.append(deletePanel(record));
    list.append(article);
  }
  setBusy(busy);
}

function loadRecords() {
  return performAction(async () => {
    const data = await api("/api/messages");
    if (!Array.isArray(data)) throw new Error("服务返回的记录格式不正确。");
    records = data;
    loaded = true;
    editingId = null;
    deletingId = null;
    renderRecords();
    showStatus(`已加载 ${records.length} 条问答。`);
  }, "正在加载聊天记录……");
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!loaded) return;
  const message = input.value.trim();
  if (!message) {
    showStatus("请先输入问题。", true);
    input.focus();
    return;
  }
  performAction(async () => {
    const record = await api("/api/messages", jsonOptions("POST", message));
    records.push(record);
    editingId = null;
    deletingId = null;
    renderRecords();
    input.value = "";
    showStatus("问答已创建。");
  }, "正在发送问题……").then(() => input.focus());
});

reloadButton.addEventListener("click", loadRecords);
loadRecords();

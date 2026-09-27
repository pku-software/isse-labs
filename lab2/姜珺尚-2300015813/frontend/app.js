"use strict";

const historyElement = document.querySelector("#messages");
const countElement = document.querySelector("#record-count");
const statusElement = document.querySelector("#page-status");
const inputElement = document.querySelector("#message-input");
let records = [];
let busy = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(text, className, onClick) {
  const node = element("button", className, text);
  node.type = "button";
  node.addEventListener("click", onClick);
  return node;
}

function setStatus(text, isError = false) {
  statusElement.textContent = text;
  statusElement.classList.toggle("is-error", isError);
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll("button, textarea").forEach((node) => {
    node.disabled = value;
  });
  historyElement.setAttribute("aria-busy", String(value));
}

async function api(path, method = "GET", data) {
  const options = { method, cache: "no-store" };
  if (data !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(data);
  }
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("无法连接服务，请确认 Flask 正在运行后重试。");
  }
  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`服务返回了无法解析的响应（HTTP ${response.status}）。`);
  }
  if (!response.ok) {
    throw new Error(result.error || `请求失败（HTTP ${response.status}）。`);
  }
  return result;
}

async function perform(pendingText, action) {
  if (busy) return;
  setBusy(true);
  setStatus(pendingText);
  try {
    await action();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    setBusy(false);
  }
}

function messageBlock(speaker, text, className) {
  const block = element("div", `message-block ${className}`);
  block.append(element("span", "speaker", speaker), element("p", "", text));
  return block;
}

function renderRecords() {
  historyElement.replaceChildren();
  countElement.textContent = `${records.length} 条记录`;
  if (records.length === 0) {
    historyElement.append(element("p", "empty-state", "还没有聊天记录。写下你的第一个问题吧。"));
    return;
  }
  for (const record of records) {
    const article = element("article", "chat-record");
    const header = element("div", "record-header");
    const actions = element("div", "record-actions");
    const tools = element("div", "record-tools");
    actions.append(
      button("修改", "text-button", () => showEditor(record, tools)),
      button("删除", "text-button delete-button", () => showDelete(record, tools)),
    );
    header.append(element("span", "record-label", `问答 #${record.id}`), actions);
    article.append(
      header,
      messageBlock("你", record.message, "user-message"),
      messageBlock("AI 助手", record.reply, "assistant-message"),
      tools,
    );
    historyElement.append(article);
  }
}

function closeTools(tools) {
  tools.replaceChildren();
  tools.closest(".chat-record").querySelector(".record-actions button").focus();
}

function showEditor(record, tools) {
  const form = element("form", "inline-panel");
  const label = element("label", "", "修改你的问题");
  const editor = element("textarea");
  editor.id = `edit-${record.id}`;
  editor.rows = 3;
  editor.value = record.message;
  label.htmlFor = editor.id;
  const actions = element("div", "record-actions inline-actions");
  const save = element("button", "primary-button", "保存修改");
  save.type = "submit";
  actions.append(save, button("取消", "text-button", () => closeTools(tools)));
  form.append(label, editor, actions);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = editor.value.trim();
    if (!message) {
      setStatus("修改内容不能为空。", true);
      editor.focus();
      return;
    }
    perform("正在保存修改…", async () => {
      const updated = await api(`/api/messages/${record.id}`, "PATCH", { message });
      records = records.map((item) => item.id === updated.id ? updated : item);
      renderRecords();
      setStatus("修改已保存。");
      inputElement.focus();
    });
  });
  tools.replaceChildren(form);
  editor.focus();
}

function showDelete(record, tools) {
  const panel = element("div", "inline-panel");
  const actions = element("div", "record-actions inline-actions");
  actions.append(
    button("确认删除", "text-button delete-button", () => {
      perform("正在删除记录…", async () => {
        await api(`/api/messages/${record.id}`, "DELETE");
        records = records.filter((item) => item.id !== record.id);
        renderRecords();
        setStatus("记录已删除。");
      });
    }),
    button("取消", "text-button", () => closeTools(tools)),
  );
  panel.append(element("p", "", "确定删除这条问答吗？删除后无法恢复。"), actions);
  tools.replaceChildren(panel);
  actions.querySelector("button").focus();
}

async function loadRecords() {
  await perform("正在加载记录…", async () => {
    const loaded = await api("/api/messages");
    if (!Array.isArray(loaded)) throw new Error("服务返回的记录格式不正确。");
    records = loaded;
    renderRecords();
    setStatus("记录已加载，可以发送新消息。");
  });
  if (countElement.textContent === "加载中") {
    countElement.textContent = "加载失败";
    historyElement.replaceChildren(element("p", "empty-state", "暂时无法加载记录，请点击“刷新记录”重试。"));
  }
}

document.querySelector("#message-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const message = inputElement.value.trim();
  if (!message) {
    setStatus("请输入消息后再发送。", true);
    inputElement.focus();
    return;
  }
  perform("正在发送消息…", async () => {
    const created = await api("/api/messages", "POST", { message });
    records.push(created);
    renderRecords();
    inputElement.value = "";
    setStatus("消息已发送，回复已显示。");
  });
});

document.querySelector("#reload-button").addEventListener("click", loadRecords);
loadRecords();

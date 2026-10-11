"use strict";

const historyElement = document.querySelector("#messages");
const countElement = document.querySelector("#record-count");
const statusElement = document.querySelector("#page-status");
const inputElement = document.querySelector("#message-input");
const conversationList = document.querySelector("#conversation-list");
const conversationTools = document.querySelector("#conversation-tools");
let conversations = [];
let selectedId = null;
let selectedTitle = "";
const drafts = new Map();
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
  node.disabled = busy;
  node.addEventListener("click", onClick);
  return node;
}

function setStatus(text, isError = false) {
  statusElement.textContent = text;
  statusElement.classList.toggle("is-error", isError);
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll("button, textarea, input").forEach((node) => {
    node.disabled = value || (node.hasAttribute("data-needs-conversation") && selectedId === null);
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
  document.querySelector("#history-title").textContent = selectedTitle || "请选择会话";
  const summary = conversations.find((item) => item.id === selectedId);
  if (summary) summary.message_count = records.length;
  renderConversations();
  historyElement.replaceChildren();
  countElement.textContent = `${records.length} 条记录`;
  if (records.length === 0) {
    historyElement.append(element("p", "empty-state", selectedId === null ? "新建或选择一个会话，开始聊天。" : "这个会话还没有记录。写下第一个问题吧。"));
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
  form.append(label, editor, element("p", "muted", "修改问题不会重新生成回答；后续提问将使用修改后的历史。"), actions);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = editor.value.trim();
    if (!message) {
      setStatus("修改内容不能为空。", true);
      editor.focus();
      return;
    }
    perform("正在保存修改…", async () => {
      const updated = await api(`/api/conversations/${selectedId}/messages/${record.id}`, "PATCH", { message });
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
        await api(`/api/conversations/${selectedId}/messages/${record.id}`, "DELETE");
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

function renderConversations() {
  conversationList.replaceChildren();
  if (!conversations.length) {
    conversationList.append(element("p", "empty-state", "还没有会话，点击“新建”开始。"));
  }
  for (const conversation of conversations) {
    const item = button("", "conversation-item", () => {
      if (selectedId === conversation.id) return;
      perform("正在切换会话…", async () => {
        const loaded = await api(`/api/conversations/${conversation.id}`);
        activateConversation(loaded);
        setStatus("会话已切换，可以继续聊天。");
      });
    });
    item.setAttribute("aria-current", conversation.id === selectedId ? "true" : "false");
    item.append(element("span", "conversation-title", conversation.title), element("span", "muted", `${conversation.message_count} 条问答`));
    conversationList.append(item);
  }
}

function activateConversation(conversation) {
  if (selectedId !== null) drafts.set(selectedId, inputElement.value);
  selectedId = conversation ? conversation.id : null;
  selectedTitle = conversation ? conversation.title : "";
  records = conversation ? conversation.messages : [];
  inputElement.value = drafts.get(selectedId) || "";
  conversationTools.replaceChildren();
  renderRecords();
  setBusy(busy);
}

async function refreshConversations() {
  await perform("正在加载会话…", async () => {
    const loaded = await api("/api/conversations");
    const preferredId = loaded.some((item) => item.id === selectedId) ? selectedId : loaded[0]?.id;
    const detail = preferredId === undefined ? null : await api(`/api/conversations/${preferredId}`);
    conversations = loaded;
    activateConversation(detail);
    setStatus(detail ? "会话已加载，可以继续聊天。" : "请先新建一个会话。");
  });
  if (countElement.textContent === "加载中") {
    countElement.textContent = "加载失败";
    conversationList.replaceChildren(element("p", "empty-state", "加载失败，请刷新会话列表重试。"));
    historyElement.replaceChildren(element("p", "empty-state", "暂时无法加载聊天记录。"));
  }
}

function showConversationForm(rename = false) {
  const targetId = rename ? selectedId : null;
  if (rename && targetId === null) return;
  const form = element("form", "conversation-form");
  const label = element("label", "", rename ? "新的会话名称" : "会话名称");
  const input = element("input");
  input.id = "conversation-title-input";
  input.type = "text";
  input.maxLength = 100;
  input.value = rename ? selectedTitle : "";
  input.placeholder = "例如：旅行计划";
  label.htmlFor = input.id;
  const actions = element("div", "record-actions inline-actions");
  const submit = element("button", "primary-button", rename ? "保存名称" : "创建会话");
  submit.type = "submit";
  actions.append(submit, button("取消", "text-button", () => conversationTools.replaceChildren()));
  form.append(label, input, actions);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const title = input.value.trim();
    if (!title) {
      setStatus("会话名称不能为空。", true);
      input.focus();
      return;
    }
    perform(rename ? "正在重命名…" : "正在创建会话…", async () => {
      const conversation = await api(rename ? `/api/conversations/${targetId}` : "/api/conversations", rename ? "PATCH" : "POST", { title });
      const summary = { id: conversation.id, title: conversation.title, message_count: conversation.messages.length };
      if (rename) {
        conversations = conversations.map((item) => item.id === targetId ? summary : item);
      } else {
        conversations.push(summary);
      }
      activateConversation(conversation);
      setStatus(rename ? "会话已重命名。" : "新会话已创建，可以发送问题。");
    });
  });
  conversationTools.replaceChildren(form);
  input.focus();
}

function showConversationDelete() {
  if (selectedId === null) return;
  const targetId = selectedId;
  const panel = element("div", "conversation-form");
  const actions = element("div", "record-actions inline-actions");
  actions.append(
    button("确认删除", "text-button delete-button", () => perform("正在删除会话…", async () => {
      await api(`/api/conversations/${targetId}`, "DELETE");
      conversations = conversations.filter((item) => item.id !== targetId);
      activateConversation(null);
      drafts.delete(targetId);
      setStatus("会话及其记录已删除，请选择或新建会话。");
    })),
    button("取消", "text-button", () => conversationTools.replaceChildren()),
  );
  panel.append(element("p", "", `确定删除“${selectedTitle}”及其全部问答吗？此操作无法恢复。`), actions);
  conversationTools.replaceChildren(panel);
  actions.querySelector("button").focus();
}

async function loadRecords() {
  if (selectedId === null) return;
  await perform("正在刷新当前会话…", async () => {
    const loaded = await api(`/api/conversations/${selectedId}`);
    const summary = conversations.find((item) => item.id === loaded.id);
    if (summary) summary.title = loaded.title;
    activateConversation(loaded);
    setStatus("当前会话已刷新。");
  });
}

document.querySelector("#message-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (selectedId === null) {
    setStatus("请先新建或选择一个会话。", true);
    return;
  }
  const message = inputElement.value.trim();
  if (!message) {
    setStatus("请输入消息后再发送。", true);
    inputElement.focus();
    return;
  }
  const targetId = selectedId;
  perform("正在生成回复，请稍候…", async () => {
    const created = await api(`/api/conversations/${targetId}/messages`, "POST", { message });
    records.push(created);
    renderRecords();
    inputElement.value = "";
    drafts.delete(targetId);
    setStatus("回复已保存，可以继续追问。");
  });
});

document.querySelector("#reload-button").addEventListener("click", loadRecords);
document.querySelector("#refresh-conversations").addEventListener("click", refreshConversations);
document.querySelector("#new-conversation").addEventListener("click", () => showConversationForm());
document.querySelector("#rename-conversation").addEventListener("click", () => showConversationForm(true));
document.querySelector("#delete-conversation").addEventListener("click", showConversationDelete);
refreshConversations();

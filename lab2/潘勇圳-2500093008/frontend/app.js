// 前端通过 fetch() 调用同一个 Flask 服务提供的 API。
// 这里用的都是以 / 开头的相对 URL，浏览器会基于当前页面的地址解析，
// 所以从 http://localhost:5001/ 打开页面时，请求也会发给这个服务。

const API_URL = "/api";

// 会话列表，以及当前选中会话的 id
let conversations = [];
let currentConversationId = null;

// 页面上的临时状态：正在重命名的会话、正在确认删除的会话/消息、正在编辑的消息
const state = {
  renamingConversation: false,
  confirmingDeleteConversation: false,
  editingMessageId: null,
  confirmingDeleteMessageId: null,
};

const els = {};

document.addEventListener("DOMContentLoaded", () => {
  els.list = document.querySelector("#conversation-list");
  els.listEmpty = document.querySelector("#conversation-empty");
  els.newButton = document.querySelector("#new-conversation");
  els.title = document.querySelector("#conversation-title");
  els.actions = document.querySelector("#conversation-actions");
  els.chat = document.querySelector("#chat");
  els.empty = document.querySelector("#empty");
  els.form = document.querySelector("#composer");
  els.input = document.querySelector("#message-input");
  els.sendButton = document.querySelector("#send-button");
  els.status = document.querySelector("#status");

  els.newButton.addEventListener("click", createConversation);
  els.form.addEventListener("submit", handleSubmit);

  // 页面打开时先加载会话列表
  loadConversations();
});

/* ---------------- 与后端通信 ---------------- */

async function requestJson(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    throw new Error("连不上后端服务，请确认 Flask 正在运行。");
  }

  const body = await response.text();
  let data = null;
  if (body) {
    try {
      data = JSON.parse(body);
    } catch (error) {
      data = null;
    }
  }

  if (!response.ok) {
    throw new Error((data && data.error) || `请求失败（HTTP ${response.status}）`);
  }
  return data;
}

async function loadConversations() {
  try {
    conversations = await requestJson(`${API_URL}/conversations`);

    // 一个会话都没有时，先建一个，页面打开就能直接用
    if (conversations.length === 0) {
      await createConversation();
      return;
    }

    if (!currentConversation()) {
      currentConversationId = conversations[0].id;
    }
    render();
  } catch (error) {
    showStatus(`加载会话失败：${error.message}`);
  }
}

async function createConversation() {
  clearStatus();
  try {
    const conversation = await requestJson(`${API_URL}/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: `新会话 ${conversations.length + 1}` }),
    });
    conversations.push(conversation);
    currentConversationId = conversation.id;
    resetTransientState();
    render();
    els.input.focus();
  } catch (error) {
    showStatus(error.message);
  }
}

async function renameConversation(value) {
  const title = value.trim();
  if (!title) {
    showStatus("会话名称不能为空。");
    return;
  }

  const conversation = currentConversation();
  if (!conversation) {
    return;
  }

  clearStatus();
  try {
    const updated = await requestJson(`${API_URL}/conversations/${conversation.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    conversations = conversations.map((item) => (item.id === updated.id ? updated : item));
    state.renamingConversation = false;
    render();
  } catch (error) {
    showStatus(error.message);
  }
}

async function deleteConversation() {
  const conversation = currentConversation();
  if (!conversation) {
    return;
  }

  clearStatus();
  try {
    await requestJson(`${API_URL}/conversations/${conversation.id}`, { method: "DELETE" });
    conversations = conversations.filter((item) => item.id !== conversation.id);
    currentConversationId = conversations.length ? conversations[0].id : null;
    resetTransientState();
    render();
  } catch (error) {
    showStatus(error.message);
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  const conversation = currentConversation();
  if (!conversation) {
    showStatus("请先新建或选择一个会话。");
    return;
  }

  const text = els.input.value.trim();
  if (!text) {
    showStatus("请先输入内容，再点击发送。");
    return;
  }

  clearStatus();
  setSending(true);
  try {
    const record = await requestJson(`${API_URL}/conversations/${conversation.id}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    conversation.messages.push(record);
    els.input.value = "";
    render();
  } catch (error) {
    showStatus(error.message);
  } finally {
    setSending(false);
  }
}

async function saveMessage(messageId, value) {
  const text = value.trim();
  if (!text) {
    showStatus("消息内容不能为空。");
    return;
  }

  const found = findLocalMessage(messageId);
  if (!found) {
    return;
  }

  clearStatus();
  try {
    const updated = await requestJson(`${API_URL}/messages/${messageId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    found.record.message = updated.message;
    found.record.reply = updated.reply;
    state.editingMessageId = null;
    render();
  } catch (error) {
    showStatus(error.message);
  }
}

async function removeMessage(messageId) {
  const found = findLocalMessage(messageId);
  if (!found) {
    return;
  }

  clearStatus();
  try {
    await requestJson(`${API_URL}/messages/${messageId}`, { method: "DELETE" });
    found.conversation.messages = found.conversation.messages.filter(
      (record) => record.id !== messageId
    );
    state.confirmingDeleteMessageId = null;
    render();
  } catch (error) {
    showStatus(error.message);
  }
}

function currentConversation() {
  return conversations.find((item) => item.id === currentConversationId) || null;
}

function findLocalMessage(messageId) {
  for (const conversation of conversations) {
    const record = conversation.messages.find((item) => item.id === messageId);
    if (record) {
      return { conversation, record };
    }
  }
  return null;
}

/* ---------------- 页面渲染 ---------------- */

function render() {
  renderConversationList();
  renderCurrentConversation();
}

function renderConversationList() {
  els.list.replaceChildren();

  conversations.forEach((conversation) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "conversation-button";
    button.title = conversation.title;
    button.textContent = conversation.title;

    if (conversation.id === currentConversationId) {
      button.classList.add("conversation-button--active");
    }

    button.addEventListener("click", () => {
      if (conversation.id === currentConversationId) {
        return;
      }
      currentConversationId = conversation.id;
      resetTransientState();
      clearStatus();
      render();
    });

    item.append(button);
    els.list.append(item);
  });

  els.listEmpty.hidden = conversations.length > 0;
}

function renderCurrentConversation() {
  const conversation = currentConversation();
  const records = conversation ? conversation.messages : [];

  els.title.textContent = conversation ? conversation.title : "未选择会话";
  renderConversationActions(conversation);

  els.chat.replaceChildren();
  records.forEach((record) => {
    els.chat.append(buildCard(record));
  });
  els.empty.hidden = !conversation || records.length > 0;

  // 没有选中会话、或正在重命名时，先不让发消息
  const disabled = !conversation || state.renamingConversation;
  els.input.disabled = disabled;
  els.sendButton.disabled = disabled;
  els.input.placeholder = conversation
    ? "输入消息，按回车或点击发送"
    : "请先新建或选择一个会话";

  // 进入消息编辑状态后，把光标直接放进输入框
  if (state.editingMessageId !== null) {
    const input = els.chat.querySelector(".editor__input");
    if (input) {
      input.focus();
      input.select();
    }
  }
}

function renderConversationActions(conversation) {
  els.actions.replaceChildren();
  if (!conversation) {
    return;
  }

  if (state.renamingConversation) {
    const input = document.createElement("input");
    input.className = "editor__input main__rename";
    input.type = "text";
    input.value = conversation.title;
    input.maxLength = 40;
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        renameConversation(input.value);
      } else if (event.key === "Escape") {
        state.renamingConversation = false;
        clearStatus();
        render();
      }
    });
    els.actions.append(
      input,
      createButton("保存", "button button--primary", () => renameConversation(input.value)),
      createButton("取消", "button button--ghost", () => {
        state.renamingConversation = false;
        clearStatus();
        render();
      })
    );
    return;
  }

  if (state.confirmingDeleteConversation) {
    els.actions.append(
      createButton("确认删除会话", "button button--danger", deleteConversation),
      createButton("取消", "button button--ghost", () => {
        state.confirmingDeleteConversation = false;
        clearStatus();
        render();
      })
    );
    return;
  }

  els.actions.append(
    createButton("重命名", "button button--ghost", () => {
      state.renamingConversation = true;
      resetMessageState();
      clearStatus();
      render();
    }),
    createButton("删除会话", "button button--ghost", () => {
      state.confirmingDeleteConversation = true;
      resetMessageState();
      clearStatus();
      render();
    })
  );
}

function buildCard(record) {
  const card = document.createElement("article");
  card.className = "message";

  const toolbar = document.createElement("div");
  toolbar.className = "message__toolbar";

  const index = document.createElement("span");
  index.className = "message__index";
  index.textContent = `#${record.id}`;

  const actions = document.createElement("div");
  actions.className = "message__actions";

  if (state.editingMessageId === record.id) {
    actions.append(
      createButton("取消", "button button--ghost", () => {
        state.editingMessageId = null;
        clearStatus();
        render();
      })
    );
  } else {
    actions.append(
      createButton("修改", "button button--ghost", () => {
        state.editingMessageId = record.id;
        state.confirmingDeleteMessageId = null;
        clearStatus();
        render();
      }),
      createButton("删除", "button button--ghost", () => {
        state.confirmingDeleteMessageId = record.id;
        state.editingMessageId = null;
        clearStatus();
        render();
      })
    );
  }

  toolbar.append(index, actions);
  card.append(toolbar);

  if (state.editingMessageId === record.id) {
    card.append(buildEditor(record));
  } else {
    card.append(buildBubble(record.message, "user"));
  }

  card.append(buildBubble(record.reply, "reply"));

  if (state.confirmingDeleteMessageId === record.id) {
    card.append(buildDeleteConfirm(record));
  }

  return card;
}

function buildEditor(record) {
  const editor = document.createElement("div");
  editor.className = "editor";

  const input = document.createElement("input");
  input.className = "editor__input";
  input.type = "text";
  input.value = record.message;
  input.maxLength = 500;
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveMessage(record.id, input.value);
    } else if (event.key === "Escape") {
      state.editingMessageId = null;
      clearStatus();
      render();
    }
  });

  editor.append(
    input,
    createButton("保存", "button button--primary", () => {
      saveMessage(record.id, input.value);
    })
  );
  return editor;
}

function buildDeleteConfirm(record) {
  const bar = document.createElement("div");
  bar.className = "confirm";

  const text = document.createElement("span");
  text.textContent = "确定要删除这条消息吗？";

  const actions = document.createElement("div");
  actions.className = "confirm__actions";
  actions.append(
    createButton("确认删除", "button button--danger", () => removeMessage(record.id)),
    createButton("取消", "button button--ghost", () => {
      state.confirmingDeleteMessageId = null;
      clearStatus();
      render();
    })
  );

  bar.append(text, actions);
  return bar;
}

function buildBubble(text, kind) {
  const bubble = document.createElement("p");
  bubble.className = kind === "user" ? "bubble bubble--user" : "bubble bubble--reply";
  bubble.textContent = text;
  return bubble;
}

function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

/* ---------------- 页面状态提示 ---------------- */

function showStatus(message) {
  els.status.textContent = message;
}

function clearStatus() {
  els.status.textContent = "";
}

function setSending(isSending) {
  els.sendButton.textContent = isSending ? "发送中…" : "发送";
  els.sendButton.disabled = isSending || !currentConversation();
}

function resetMessageState() {
  state.editingMessageId = null;
  state.confirmingDeleteMessageId = null;
}

function resetTransientState() {
  state.renamingConversation = false;
  state.confirmingDeleteConversation = false;
  resetMessageState();
}

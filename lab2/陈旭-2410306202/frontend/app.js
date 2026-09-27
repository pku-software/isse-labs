// 前端逻辑：用 fetch() 调用同一个 Flask 服务提供的会话 API。
// 所有请求都写成相对 URL（例如 "/api/conversations"），
// 浏览器会自动把它接到当前页面的地址上，所以不需要写死 http://localhost:5001。

const statusEl = document.getElementById("status");
const conversationListEl = document.getElementById("conversation-list");
const sidebarEmptyEl = document.getElementById("sidebar-empty");
const newConversationButton = document.getElementById("new-conversation-button");
const titleAreaEl = document.getElementById("title-area");
const renameButton = document.getElementById("rename-conversation-button");
const deleteConversationButton = document.getElementById("delete-conversation-button");
const chatHeadExtraEl = document.getElementById("chat-head-extra");
const chatList = document.getElementById("chat-list");
const emptyState = document.getElementById("empty-state");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

// 侧边栏用的会话摘要列表：[{id, title, turn_count}]
let conversations = [];

// 当前选中会话的完整内容：{id, title, turns: [{id, message, reply}]}
let current = null;

// ---------- 小工具 ----------

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("is-error", isError);
}

// 统一处理请求：解析 JSON，把非 2xx 的响应变成异常，交给调用处显示在页面上
async function request(url, options = {}) {
  const response = await fetch(url, options);

  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    const reason = data && data.error ? data.error : `请求失败（HTTP ${response.status}）`;
    throw new Error(reason);
  }

  return data;
}

function createButton(className, text) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `btn ${className}`;
  button.textContent = text;
  return button;
}

function createBubble(className, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${className}`;

  const paragraph = document.createElement("p");
  paragraph.className = "bubble-text";
  // 用 textContent 而不是 innerHTML：内容只作为文本显示，不会被当成 HTML 执行
  paragraph.textContent = text;

  bubble.appendChild(paragraph);
  return bubble;
}

// ---------- 渲染 ----------

function renderConversationList() {
  conversationListEl.innerHTML = "";

  if (conversations.length === 0) {
    sidebarEmptyEl.hidden = false;
    return;
  }

  sidebarEmptyEl.hidden = true;

  conversations.forEach((item) => {
    const listItem = document.createElement("li");

    const button = document.createElement("button");
    button.type = "button";
    button.className = "conversation-item";
    if (current && current.id === item.id) {
      button.classList.add("is-active");
    }

    const title = document.createElement("span");
    title.className = "conversation-item-title";
    title.textContent = item.title;

    const meta = document.createElement("span");
    meta.className = "conversation-item-meta";
    meta.textContent = `${item.turn_count} 轮对话`;

    button.appendChild(title);
    button.appendChild(meta);
    button.addEventListener("click", () => selectConversation(item.id));

    listItem.appendChild(button);
    conversationListEl.appendChild(listItem);
  });
}

function renderTitleArea() {
  titleAreaEl.innerHTML = "";

  const heading = document.createElement("h2");
  heading.className = "chat-title";
  heading.id = "conversation-title";
  heading.textContent = current ? current.title : "未选择会话";

  titleAreaEl.appendChild(heading);
}

function renderChat() {
  const hasConversation = current !== null;

  renderTitleArea();

  renameButton.disabled = !hasConversation;
  deleteConversationButton.disabled = !hasConversation;
  sendButton.disabled = !hasConversation;
  messageInput.disabled = !hasConversation;

  if (hasConversation) {
    messageInput.placeholder = "输入你的问题，按发送加入当前会话";
  } else {
    messageInput.placeholder = "先新建或选择一个会话";
  }

  chatList.querySelectorAll(".message").forEach((node) => node.remove());

  if (!hasConversation) {
    emptyState.hidden = false;
    emptyState.textContent = "先新建或选择一个会话。";
    return;
  }

  if (current.turns.length === 0) {
    emptyState.hidden = false;
    emptyState.textContent = "这个会话还没有对话，在下面输入一句话试试。";
    return;
  }

  emptyState.hidden = true;
  current.turns.forEach((turn) => {
    chatList.appendChild(createTurnElement(turn));
  });
}

function createTurnElement(turn) {
  const article = document.createElement("article");
  article.className = "message";
  article.dataset.id = turn.id;

  article.appendChild(createBubble("bubble-user", turn.message));
  article.appendChild(createBubble("bubble-reply", turn.reply));

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editButton = createButton("btn-edit", "修改");
  editButton.addEventListener("click", () => startEditTurn(article, turn));

  const deleteButton = createButton("btn-delete", "删除");
  deleteButton.addEventListener("click", () => startDeleteTurn(article, turn, actions));

  actions.appendChild(editButton);
  actions.appendChild(deleteButton);
  article.appendChild(actions);

  return article;
}

// 用后端返回的最新会话刷新页面，并同步侧边栏的标题和轮数
function applyConversation(conversation) {
  current = conversation;
  chatHeadExtraEl.innerHTML = "";

  conversations = conversations.map((item) =>
    item.id === conversation.id
      ? { ...item, title: conversation.title, turn_count: conversation.turns.length }
      : item
  );

  renderConversationList();
  renderChat();
}

// ---------- 会话操作 ----------

async function loadConversations(preferredId = null) {
  setStatus("正在加载会话列表…");

  try {
    conversations = await request("/api/conversations");
  } catch (error) {
    setStatus(`加载会话列表失败：${error.message}`, true);
    return;
  }

  let targetId = preferredId;
  if (targetId === null) {
    if (current && conversations.some((item) => item.id === current.id)) {
      targetId = current.id;
    } else if (conversations.length > 0) {
      targetId = conversations[conversations.length - 1].id;
    }
  }

  if (targetId === null) {
    current = null;
    renderConversationList();
    renderChat();
    setStatus("");
    return;
  }

  await selectConversation(targetId);
}

async function selectConversation(conversationId) {
  setStatus("正在加载会话…");

  try {
    current = await request(`/api/conversations/${conversationId}`);
    chatHeadExtraEl.innerHTML = "";
    renderConversationList();
    renderChat();
    setStatus("");
  } catch (error) {
    setStatus(`加载会话失败：${error.message}`, true);
  }
}

async function createConversation() {
  setStatus("正在新建会话…");

  try {
    const conversation = await request("/api/conversations", { method: "POST" });
    await loadConversations(conversation.id);
    setStatus(`已新建会话「${conversation.title}」`);
  } catch (error) {
    setStatus(`新建会话失败：${error.message}`, true);
  }
}

function startRenameConversation() {
  if (!current) {
    return;
  }

  titleAreaEl.innerHTML = "";

  const input = document.createElement("input");
  input.type = "text";
  input.className = "title-input";
  input.value = current.title;
  input.setAttribute("aria-label", "会话名称");

  const saveButton = createButton("btn-primary", "保存");
  const cancelButton = createButton("btn-cancel", "取消");

  cancelButton.addEventListener("click", () => {
    renderTitleArea();
    setStatus("");
  });

  saveButton.addEventListener("click", async () => {
    const title = input.value.trim();
    if (!title) {
      setStatus("会话名称不能为空", true);
      return;
    }

    saveButton.disabled = true;
    setStatus("正在保存会话名称…");

    try {
      const conversation = await request(`/api/conversations/${current.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      });
      applyConversation(conversation);
      setStatus("会话名称已更新");
    } catch (error) {
      saveButton.disabled = false;
      setStatus(`重命名失败：${error.message}`, true);
    }
  });

  titleAreaEl.appendChild(input);
  titleAreaEl.appendChild(saveButton);
  titleAreaEl.appendChild(cancelButton);

  input.focus();
  input.select();
}

function startDeleteConversation() {
  if (!current) {
    return;
  }

  chatHeadExtraEl.innerHTML = "";

  const row = document.createElement("div");
  row.className = "confirm-row";

  const question = document.createElement("span");
  question.textContent = `确定删除会话「${current.title}」及其全部对话吗？`;

  const confirmButton = createButton("btn-danger", "确定删除");
  const cancelButton = createButton("btn-cancel", "取消");

  cancelButton.addEventListener("click", () => {
    chatHeadExtraEl.innerHTML = "";
  });

  confirmButton.addEventListener("click", async () => {
    confirmButton.disabled = true;
    setStatus("正在删除会话…");

    try {
      await request(`/api/conversations/${current.id}`, { method: "DELETE" });
      chatHeadExtraEl.innerHTML = "";
      current = null;
      await loadConversations();
      setStatus("会话已删除");
    } catch (error) {
      confirmButton.disabled = false;
      setStatus(`删除会话失败：${error.message}`, true);
    }
  });

  row.appendChild(question);
  row.appendChild(confirmButton);
  row.appendChild(cancelButton);
  chatHeadExtraEl.appendChild(row);
}

// ---------- 发送新问题：带上当前会话的历史一起发给后端 ----------

async function sendMessage() {
  if (!current) {
    setStatus("请先新建或选择一个会话", true);
    return;
  }

  const text = messageInput.value.trim();
  if (!text) {
    setStatus("请先输入内容再发送", true);
    return;
  }

  sendButton.disabled = true;
  setStatus("正在等待模型回复…");

  try {
    const conversation = await request(`/api/conversations/${current.id}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    messageInput.value = "";
    applyConversation(conversation);
    setStatus("已收到模型回复");
  } catch (error) {
    setStatus(`发送失败：${error.message}`, true);
  } finally {
    sendButton.disabled = !current;
  }
}

// ---------- 修改某一轮提问：页面内编辑区，不用 prompt() ----------

function startEditTurn(article, turn) {
  const actions = article.querySelector(".message-actions");
  actions.hidden = true;

  const editArea = document.createElement("div");
  editArea.className = "edit-area";

  const label = document.createElement("label");
  label.className = "edit-label";
  label.textContent = "修改这一轮提问";
  label.htmlFor = `edit-input-${turn.id}`;

  const textarea = document.createElement("textarea");
  textarea.id = `edit-input-${turn.id}`;
  textarea.className = "edit-input";
  textarea.rows = 2;
  textarea.value = turn.message;

  const errorLine = document.createElement("p");
  errorLine.className = "edit-error";

  const editActions = document.createElement("div");
  editActions.className = "edit-actions";

  const saveButton = createButton("btn-primary", "保存");
  const cancelButton = createButton("btn-cancel", "取消");

  cancelButton.addEventListener("click", () => {
    editArea.remove();
    actions.hidden = false;
  });

  saveButton.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (!text) {
      errorLine.textContent = "修改后的内容不能为空";
      return;
    }

    saveButton.disabled = true;
    setStatus("正在保存修改…");

    try {
      const conversation = await request(
        `/api/conversations/${current.id}/turns/${turn.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        }
      );
      applyConversation(conversation);
      setStatus("已修改这一轮提问");
    } catch (error) {
      saveButton.disabled = false;
      errorLine.textContent = error.message;
      setStatus(`修改失败：${error.message}`, true);
    }
  });

  editActions.appendChild(saveButton);
  editActions.appendChild(cancelButton);
  editArea.appendChild(label);
  editArea.appendChild(textarea);
  editArea.appendChild(errorLine);
  editArea.appendChild(editActions);
  article.appendChild(editArea);

  textarea.focus();
}

// ---------- 删除某一轮问答：页面内确认行，不用 confirm() ----------

function startDeleteTurn(article, turn, actions) {
  actions.hidden = true;

  const row = document.createElement("div");
  row.className = "confirm-row";

  const question = document.createElement("span");
  question.textContent = `确定删除这一轮对话吗？（第 ${turn.id} 轮）`;

  const confirmButton = createButton("btn-danger", "确定删除");
  const cancelButton = createButton("btn-cancel", "取消");

  cancelButton.addEventListener("click", () => {
    row.remove();
    actions.hidden = false;
  });

  confirmButton.addEventListener("click", async () => {
    confirmButton.disabled = true;
    setStatus("正在删除…");

    try {
      const conversation = await request(
        `/api/conversations/${current.id}/turns/${turn.id}`,
        { method: "DELETE" }
      );
      applyConversation(conversation);
      setStatus("已删除这一轮对话");
    } catch (error) {
      confirmButton.disabled = false;
      setStatus(`删除失败：${error.message}`, true);
    }
  });

  row.appendChild(question);
  row.appendChild(confirmButton);
  row.appendChild(cancelButton);
  article.appendChild(row);
}

// ---------- 启动 ----------

newConversationButton.addEventListener("click", createConversation);
renameButton.addEventListener("click", startRenameConversation);
deleteConversationButton.addEventListener("click", startDeleteConversation);
sendButton.addEventListener("click", sendMessage);

renderChat();
loadConversations();

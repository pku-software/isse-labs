const conversationForm = document.querySelector("#conversation-form");
const conversationTitleInput = document.querySelector("#conversation-title");
const conversationList = document.querySelector("#conversation-list");
const currentConversationTitle = document.querySelector("#current-conversation-title");
const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const feedback = document.querySelector("#page-feedback");

let conversations = [];
let activeConversation = null;
let renamingConversationId = null;
let deletingConversationId = null;
let editingMessageId = null;
let deletingMessageId = null;

function showFeedback(text = "", type = "") {
  feedback.textContent = text;
  feedback.className = `page-feedback ${type}`.trim();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）`);
  }
  return data;
}

function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

function replaceConversation(updated) {
  conversations = conversations.map((item) =>
    item.id === updated.id ? updated : item,
  );
  if (activeConversation?.id === updated.id) {
    activeConversation = updated;
  }
}

function updateComposerState() {
  const disabled = activeConversation === null;
  messageInput.disabled = disabled;
  sendButton.disabled = disabled;
  currentConversationTitle.textContent = activeConversation
    ? activeConversation.title
    : "请选择会话";
}

async function selectConversation(conversationId) {
  try {
    activeConversation = await apiRequest(
      `/api/conversations/${conversationId}`,
    );
    replaceConversation(activeConversation);
    renamingConversationId = null;
    deletingConversationId = null;
    editingMessageId = null;
    deletingMessageId = null;
    showFeedback();
    renderConversationList();
    renderMessages();
    updateComposerState();
    messageInput.focus();
  } catch (error) {
    showFeedback(error.message, "error");
  }
}

function renderRenamePanel(conversation, item) {
  const panel = document.createElement("div");
  panel.className = "conversation-inline-panel";

  const input = document.createElement("input");
  input.type = "text";
  input.maxLength = 60;
  input.value = conversation.title;
  input.setAttribute("aria-label", "新的会话名称");

  const saveButton = createButton("保存", "mini-button", async () => {
    const title = input.value.trim();
    if (!title) {
      showFeedback("会话名称不能为空。", "error");
      input.focus();
      return;
    }

    saveButton.disabled = true;
    try {
      const updated = await apiRequest(
        `/api/conversations/${conversation.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title }),
        },
      );
      replaceConversation(updated);
      renamingConversationId = null;
      showFeedback("会话已重命名。", "success");
      renderConversationList();
      updateComposerState();
    } catch (error) {
      showFeedback(error.message, "error");
      saveButton.disabled = false;
    }
  });

  const cancelButton = createButton("取消", "mini-button secondary", () => {
    renamingConversationId = null;
    showFeedback();
    renderConversationList();
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveButton.click();
    }
  });

  panel.append(input, saveButton, cancelButton);
  item.append(panel);
  window.requestAnimationFrame(() => input.focus());
}

function renderConversationDeletePanel(conversation, item) {
  const panel = document.createElement("div");
  panel.className = "conversation-confirm-panel";

  const prompt = document.createElement("p");
  prompt.textContent = "删除会话及全部消息？";

  const confirmButton = createButton(
    "确认",
    "mini-button danger",
    async () => {
      confirmButton.disabled = true;
      try {
        await apiRequest(`/api/conversations/${conversation.id}`, {
          method: "DELETE",
        });
        conversations = conversations.filter(
          (item) => item.id !== conversation.id,
        );
        deletingConversationId = null;

        if (activeConversation?.id === conversation.id) {
          activeConversation = null;
          if (conversations.length > 0) {
            await selectConversation(conversations[0].id);
          } else {
            renderConversationList();
            renderMessages();
            updateComposerState();
            showFeedback("会话已删除。", "success");
          }
        } else {
          renderConversationList();
          showFeedback("会话已删除。", "success");
        }
      } catch (error) {
        showFeedback(error.message, "error");
        confirmButton.disabled = false;
      }
    },
  );

  const cancelButton = createButton("取消", "mini-button secondary", () => {
    deletingConversationId = null;
    showFeedback();
    renderConversationList();
  });

  panel.append(prompt, confirmButton, cancelButton);
  item.append(panel);
}

function renderConversationList() {
  conversationList.replaceChildren();

  if (conversations.length === 0) {
    const empty = document.createElement("p");
    empty.className = "sidebar-empty";
    empty.textContent = "还没有会话，请先新建一个。";
    conversationList.append(empty);
    return;
  }

  for (const conversation of conversations) {
    const item = document.createElement("article");
    item.className = "conversation-item";
    if (activeConversation?.id === conversation.id) {
      item.classList.add("active");
    }

    const mainRow = document.createElement("div");
    mainRow.className = "conversation-main-row";

    const selectButton = createButton(
      conversation.title,
      "conversation-select",
      () => selectConversation(conversation.id),
    );
    const actions = document.createElement("div");
    actions.className = "conversation-actions";
    actions.append(
      createButton("改名", "icon-button", () => {
        renamingConversationId = conversation.id;
        deletingConversationId = null;
        showFeedback();
        renderConversationList();
      }),
      createButton("删除", "icon-button danger", () => {
        deletingConversationId = conversation.id;
        renamingConversationId = null;
        showFeedback();
        renderConversationList();
      }),
    );
    mainRow.append(selectButton, actions);
    item.append(mainRow);

    if (renamingConversationId === conversation.id) {
      renderRenamePanel(conversation, item);
    } else if (deletingConversationId === conversation.id) {
      renderConversationDeletePanel(conversation, item);
    }
    conversationList.append(item);
  }
}

function createMessageRow(role, text, className) {
  const row = document.createElement("div");
  row.className = `message-row ${className}`;

  const roleLabel = document.createElement("span");
  roleLabel.className = "role-label";
  roleLabel.textContent = role;

  const content = document.createElement("p");
  content.textContent = text;

  row.append(roleLabel, content);
  return row;
}

async function refreshActiveConversation() {
  if (!activeConversation) {
    return;
  }
  const updated = await apiRequest(
    `/api/conversations/${activeConversation.id}`,
  );
  replaceConversation(updated);
  renderConversationList();
  renderMessages();
  updateComposerState();
}

function renderMessageEditPanel(message, card) {
  const panel = document.createElement("div");
  panel.className = "edit-panel";

  const input = document.createElement("input");
  input.className = "edit-input";
  input.type = "text";
  input.value = message.content;
  input.setAttribute("aria-label", "修改消息内容");

  const saveButton = createButton("保存", "action-button", async () => {
    const newText = input.value.trim();
    if (!newText) {
      showFeedback("修改内容不能为空。", "error");
      input.focus();
      return;
    }

    saveButton.disabled = true;
    try {
      await apiRequest(`/api/messages/${message.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newText }),
      });
      editingMessageId = null;
      await refreshActiveConversation();
      showFeedback("聊天记录已修改。", "success");
    } catch (error) {
      showFeedback(error.message, "error");
      saveButton.disabled = false;
    }
  });

  const cancelButton = createButton("取消", "action-button secondary", () => {
    editingMessageId = null;
    showFeedback();
    renderMessages();
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveButton.click();
    }
  });

  panel.append(input, saveButton, cancelButton);
  card.append(panel);
  window.requestAnimationFrame(() => input.focus());
}

function renderMessageDeletePanel(message, card) {
  const panel = document.createElement("div");
  panel.className = "delete-panel";

  const prompt = document.createElement("p");
  prompt.textContent = "确定删除这一轮问答吗？";

  const confirmButton = createButton(
    "确认删除",
    "action-button danger",
    async () => {
      confirmButton.disabled = true;
      try {
        await apiRequest(`/api/messages/${message.id}`, {
          method: "DELETE",
        });
        deletingMessageId = null;
        await refreshActiveConversation();
        showFeedback("这一轮问答已删除。", "success");
      } catch (error) {
        showFeedback(error.message, "error");
        confirmButton.disabled = false;
      }
    },
  );

  const cancelButton = createButton("取消", "action-button secondary", () => {
    deletingMessageId = null;
    showFeedback();
    renderMessages();
  });

  panel.append(prompt, confirmButton, cancelButton);
  card.append(panel);
}

function renderMessages() {
  messageList.replaceChildren();

  if (!activeConversation) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "请先创建或选择一个会话。";
    messageList.append(empty);
    return;
  }

  if (activeConversation.messages.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "当前会话还没有消息，开始提问吧。";
    messageList.append(empty);
    return;
  }

  for (let index = 0; index < activeConversation.messages.length; index += 1) {
    const message = activeConversation.messages[index];

    if (message.role === "assistant") {
      const card = document.createElement("article");
      card.className = "message-card";
      card.append(createMessageRow("AI", message.content, "assistant-message"));
      messageList.append(card);
      continue;
    }

    const card = document.createElement("article");
    card.className = "message-card";
    card.append(createMessageRow("你", message.content, "user-message"));

    const nextMessage = activeConversation.messages[index + 1];
    if (nextMessage?.role === "assistant") {
      card.append(
        createMessageRow("AI", nextMessage.content, "assistant-message"),
      );
      index += 1;
    }

    const actions = document.createElement("div");
    actions.className = "message-actions";
    actions.setAttribute("aria-label", "聊天记录操作");
    actions.append(
      createButton("修改", "text-button", () => {
        editingMessageId = message.id;
        deletingMessageId = null;
        showFeedback();
        renderMessages();
      }),
      createButton("删除", "text-button danger", () => {
        deletingMessageId = message.id;
        editingMessageId = null;
        showFeedback();
        renderMessages();
      }),
    );
    card.append(actions);

    if (editingMessageId === message.id) {
      renderMessageEditPanel(message, card);
    } else if (deletingMessageId === message.id) {
      renderMessageDeletePanel(message, card);
    }
    messageList.append(card);
  }
}

conversationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = conversationTitleInput.value.trim();

  try {
    const created = await apiRequest("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    conversations.push(created);
    conversationTitleInput.value = "";
    showFeedback("新会话已创建。", "success");
    await selectConversation(created.id);
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!activeConversation) {
    showFeedback("请先选择一个会话。", "error");
    return;
  }

  const text = messageInput.value.trim();
  if (!text) {
    showFeedback("请先输入消息。", "error");
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  showFeedback("正在等待 DeepSeek 回复……");
  try {
    const updated = await apiRequest(
      `/api/conversations/${activeConversation.id}/messages`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      },
    );
    replaceConversation(updated);
    messageInput.value = "";
    renderConversationList();
    renderMessages();
    showFeedback("回复已收到。", "success");
    messageInput.focus();
  } catch (error) {
    showFeedback(error.message, "error");
  } finally {
    sendButton.disabled = false;
  }
});

async function loadConversations() {
  try {
    conversations = await apiRequest("/api/conversations");
    renderConversationList();
    if (conversations.length > 0) {
      await selectConversation(conversations[0].id);
    } else {
      activeConversation = null;
      renderMessages();
      updateComposerState();
    }
  } catch (error) {
    conversationList.replaceChildren();
    activeConversation = null;
    renderMessages();
    updateComposerState();
    showFeedback(error.message, "error");
  }
}

loadConversations();

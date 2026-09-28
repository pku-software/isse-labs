const conversationForm = document.querySelector("#conversation-form");
const conversationInput = document.querySelector("#conversation-input");
const conversationList = document.querySelector("#conversation-list");
const historyTitle = document.querySelector("#history-title");
const historyDescription = document.querySelector("#history-description");
const messageList = document.querySelector("#message-list");
const recordCount = document.querySelector("#record-count");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const formStatus = document.querySelector("#form-status");

let conversations = [];
let activeConversation = null;

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

function replaceConversationSummary(summary) {
  conversations = conversations.map((item) =>
    item.id === summary.id ? summary : item,
  );
}

function clearActiveConversation() {
  activeConversation = null;
  historyTitle.textContent = "请选择一个会话";
  historyDescription.textContent = "创建或选择会话后即可开始聊天。";
  recordCount.textContent = "0 轮对话";
  messageInput.disabled = true;
  messageInput.placeholder = "先创建或选择一个会话";
  sendButton.disabled = true;

  const emptyState = document.createElement("p");
  emptyState.className = "empty-state";
  emptyState.textContent = "当前没有选中的会话。";
  messageList.replaceChildren(emptyState);
  setStatus("请先创建或选择会话。");
}

function showConversationRenamer(container, conversation) {
  container.querySelector(".conversation-inline-form")?.remove();

  const form = document.createElement("form");
  form.className = "conversation-inline-form";
  const input = document.createElement("input");
  input.value = conversation.title;
  input.maxLength = 60;
  input.setAttribute("aria-label", "新的会话名称");

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(createButton("取消", "button-secondary", () => form.remove()));

  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.className = "button button-primary";
  saveButton.textContent = "保存";
  actions.append(saveButton);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = input.value.trim();
    if (!title) {
      setStatus("会话名称不能为空。", "error");
      input.focus();
      return;
    }

    try {
      const updated = await requestJson(`/api/conversations/${conversation.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      });
      replaceConversationSummary(updated);
      if (activeConversation?.id === updated.id) {
        activeConversation.title = updated.title;
        historyTitle.textContent = updated.title;
      }
      renderConversations();
      setStatus("会话名称已更新。", "success");
    } catch (error) {
      setStatus(error.message, "error");
    }
  });

  form.append(input, actions);
  container.append(form);
  input.focus();
}

function showConversationDeleteConfirmation(container, conversation) {
  container.querySelector(".conversation-inline-form")?.remove();

  const confirmation = document.createElement("div");
  confirmation.className = "conversation-inline-form delete-confirmation";
  const text = document.createElement("p");
  text.textContent = "删除会话及其中全部消息？";

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createButton("取消", "button-secondary", () => confirmation.remove()),
    createButton("确认删除", "button-danger", async () => {
      try {
        await requestJson(`/api/conversations/${conversation.id}`, {
          method: "DELETE",
        });
        conversations = conversations.filter((item) => item.id !== conversation.id);
        if (activeConversation?.id === conversation.id) {
          clearActiveConversation();
        }
        renderConversations();
        if (!activeConversation && conversations.length > 0) {
          await selectConversation(conversations[0].id);
        }
        setStatus("会话已删除。", "success");
      } catch (error) {
        setStatus(error.message, "error");
      }
    }),
  );

  confirmation.append(text, actions);
  container.append(confirmation);
}

function createConversationItem(conversation) {
  const item = document.createElement("article");
  item.className = "conversation-item";
  if (activeConversation?.id === conversation.id) {
    item.classList.add("is-active");
  }

  const selectButton = document.createElement("button");
  selectButton.type = "button";
  selectButton.className = "conversation-select";
  selectButton.addEventListener("click", () => selectConversation(conversation.id));

  const title = document.createElement("strong");
  title.textContent = conversation.title;
  const count = document.createElement("span");
  count.textContent = `${Math.floor(conversation.message_count / 2)} 轮对话`;
  selectButton.append(title, count);

  const actions = document.createElement("div");
  actions.className = "conversation-actions";
  actions.append(
    createButton("重命名", "button-secondary", () =>
      showConversationRenamer(item, conversation),
    ),
    createButton("删除", "button-danger", () =>
      showConversationDeleteConfirmation(item, conversation),
    ),
  );

  item.append(selectButton, actions);
  return item;
}

function renderConversations() {
  conversationList.replaceChildren();
  if (conversations.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "还没有会话，请先创建一个。";
    conversationList.append(emptyState);
    return;
  }

  conversations.forEach((conversation) => {
    conversationList.append(createConversationItem(conversation));
  });
}

function groupMessagesByTurn(messages) {
  const turns = [];
  messages.forEach((message) => {
    let turn = turns.find((item) => item.turnId === message.turn_id);
    if (!turn) {
      turn = { turnId: message.turn_id };
      turns.push(turn);
    }
    turn[message.role] = message;
  });
  return turns;
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

function showMessageEditor(card, userMessage) {
  card.querySelector(".message-editor")?.remove();
  card.querySelector(".delete-confirmation")?.remove();

  const editor = document.createElement("form");
  editor.className = "message-editor";
  const textarea = document.createElement("textarea");
  textarea.value = userMessage.content;
  textarea.setAttribute("aria-label", "修改用户消息");

  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(createButton("取消", "button-secondary", () => editor.remove()));
  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.className = "button button-primary";
  saveButton.textContent = "保存修改";
  actions.append(saveButton);

  editor.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = textarea.value.trim();
    if (!message) {
      setStatus("修改内容不能为空。", "error");
      textarea.focus();
      return;
    }

    try {
      const updated = await requestJson(
        `/api/conversations/${activeConversation.id}/messages/${userMessage.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        },
      );
      activeConversation.messages = activeConversation.messages.map((item) =>
        item.id === updated.id ? updated : item,
      );
      renderMessages();
      setStatus("用户消息已修改，原模型回复保持不变。", "success");
    } catch (error) {
      setStatus(error.message, "error");
    }
  });

  editor.append(textarea, actions);
  card.append(editor);
  textarea.focus();
}

function showMessageDeleteConfirmation(card, userMessage) {
  card.querySelector(".message-editor")?.remove();
  card.querySelector(".delete-confirmation")?.remove();

  const confirmation = document.createElement("div");
  confirmation.className = "delete-confirmation";
  const text = document.createElement("p");
  text.textContent = "确定删除这一轮问题和回答吗？";
  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createButton("取消", "button-secondary", () => confirmation.remove()),
    createButton("确认删除", "button-danger", async () => {
      try {
        await requestJson(
          `/api/conversations/${activeConversation.id}/messages/${userMessage.id}`,
          { method: "DELETE" },
        );
        activeConversation.messages = activeConversation.messages.filter(
          (item) => item.turn_id !== userMessage.turn_id,
        );
        updateActiveSummary();
        renderMessages();
        renderConversations();
        setStatus("这一轮对话已删除。", "success");
      } catch (error) {
        setStatus(error.message, "error");
      }
    }),
  );
  confirmation.append(text, actions);
  card.append(confirmation);
}

function createMessageCard(turn) {
  const card = document.createElement("article");
  card.className = "message-card";
  const content = document.createElement("div");
  content.className = "message-content";
  if (turn.user) {
    content.append(createMessageLine("你", turn.user.content));
  }
  if (turn.assistant) {
    content.append(createMessageLine("AI", turn.assistant.content, true));
  }

  const actions = document.createElement("div");
  actions.className = "message-actions";
  actions.setAttribute("aria-label", "这一轮对话的操作");
  if (turn.user) {
    actions.append(
      createButton("修改", "button-secondary", () =>
        showMessageEditor(card, turn.user),
      ),
      createButton("删除", "button-danger", () =>
        showMessageDeleteConfirmation(card, turn.user),
      ),
    );
  }
  card.append(content, actions);
  return card;
}

function renderMessages() {
  messageList.replaceChildren();
  const messages = activeConversation?.messages || [];
  const turns = groupMessagesByTurn(messages);
  recordCount.textContent = `${turns.length} 轮对话`;

  if (turns.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "当前会话还没有消息，发送第一条吧。";
    messageList.append(emptyState);
    return;
  }
  turns.forEach((turn) => messageList.append(createMessageCard(turn)));
}

function updateActiveSummary() {
  if (!activeConversation) {
    return;
  }
  replaceConversationSummary({
    id: activeConversation.id,
    title: activeConversation.title,
    message_count: activeConversation.messages.length,
  });
}

async function selectConversation(conversationId) {
  try {
    activeConversation = await requestJson(`/api/conversations/${conversationId}`);
    historyTitle.textContent = activeConversation.title;
    historyDescription.textContent = "模型会使用这个会话中的历史消息作为上下文。";
    messageInput.disabled = false;
    messageInput.placeholder = "输入你想继续聊的内容";
    sendButton.disabled = false;
    renderConversations();
    renderMessages();
    setStatus("会话已加载。", "success");
    messageInput.focus();
  } catch (error) {
    setStatus(error.message, "error");
  }
}

async function loadConversations() {
  try {
    conversations = await requestJson("/api/conversations");
    renderConversations();
    if (conversations.length > 0) {
      await selectConversation(conversations[0].id);
    } else {
      clearActiveConversation();
    }
  } catch (error) {
    clearActiveConversation();
    setStatus(error.message, "error");
  }
}

conversationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = conversationInput.value.trim();

  try {
    const created = await requestJson("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    conversations.push({ id: created.id, title: created.title, message_count: 0 });
    conversationForm.reset();
    renderConversations();
    await selectConversation(created.id);
    setStatus("新会话已创建。", "success");
  } catch (error) {
    setStatus(error.message, "error");
  }
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!activeConversation) {
    setStatus("请先创建或选择会话。", "error");
    return;
  }

  const message = messageInput.value.trim();
  if (!message) {
    setStatus("请输入消息内容。", "error");
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  setStatus("正在发送，会话历史会一并提供给模型……");
  try {
    const created = await requestJson(
      `/api/conversations/${activeConversation.id}/messages`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      },
    );
    activeConversation.messages.push(created.user_message, created.assistant_message);
    updateActiveSummary();
    renderMessages();
    renderConversations();
    messageForm.reset();
    setStatus("消息已发送，模型已结合当前会话历史回复。", "success");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    sendButton.disabled = false;
  }
});

loadConversations();

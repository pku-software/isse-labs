const chat = document.querySelector("#chat");
const composer = document.querySelector("#composer");
const messageInput = document.querySelector("#message-input");
const feedback = document.querySelector("#feedback");
const status = document.querySelector("#status");

function showFeedback(text) {
  feedback.textContent = text;
}

async function readError(response) {
  try {
    const data = await response.json();
    return data.error || "请求失败";
  } catch (_error) {
    return "请求失败";
  }
}

function renderRecords(records) {
  chat.replaceChildren();
  if (records.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "还没有聊天记录。";
    chat.append(empty);
    return;
  }
  for (const record of records) {
    chat.append(createRecord(record));
  }
}

function createRecord(record) {
  const article = document.createElement("article");
  article.className = "record";

  const main = document.createElement("div");
  main.className = "record-main";
  main.append(
    labeledText("你", record.message, "text"),
    labeledText("回复", record.reply, "text reply")
  );

  const actions = document.createElement("div");
  actions.className = "record-actions";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.textContent = "修改";
  editButton.addEventListener("click", () => startEdit(article, record));

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "danger";
  deleteButton.textContent = "删除";
  deleteButton.addEventListener("click", () => startDelete(article, record));

  actions.append(editButton, deleteButton);
  article.append(main, actions);
  return article;
}

function labeledText(role, text, className) {
  const block = document.createElement("div");
  const roleNode = document.createElement("p");
  roleNode.className = "role";
  roleNode.textContent = role;
  const textNode = document.createElement("p");
  textNode.className = className;
  textNode.textContent = text;
  block.append(roleNode, textNode);
  return block;
}

function startEdit(article, record) {
  const editor = document.createElement("form");
  editor.className = "inline-editor";

  const label = document.createElement("label");
  label.textContent = "修改消息";

  const input = document.createElement("textarea");
  input.rows = 3;
  input.value = record.message;

  const hint = document.createElement("p");
  hint.className = "feedback";

  const save = document.createElement("button");
  save.type = "submit";
  save.textContent = "保存";

  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "secondary";
  cancel.textContent = "取消";
  cancel.addEventListener("click", () => {
    loadMessages();
  });

  const bar = document.createElement("div");
  bar.className = "inline-actions";
  bar.append(hint, cancel, save);
  editor.append(label, input, bar);

  editor.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) {
      hint.textContent = "消息不能为空。";
      return;
    }
    const response = await fetch(`/api/messages/${record.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    if (!response.ok) {
      hint.textContent = await readError(response);
      return;
    }
    showFeedback("已修改。");
    await loadMessages();
  });

  article.replaceChildren(editor);
}

function startDelete(article, record) {
  const panel = document.createElement("div");
  panel.className = "confirm-panel";

  const hint = document.createElement("p");
  hint.className = "feedback";
  hint.textContent = "确认删除这条记录？";

  const confirm = document.createElement("button");
  confirm.type = "button";
  confirm.className = "danger";
  confirm.textContent = "确认删除";
  confirm.addEventListener("click", async () => {
    const response = await fetch(`/api/messages/${record.id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      hint.textContent = await readError(response);
      return;
    }
    showFeedback("已删除。");
    await loadMessages();
  });

  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "secondary";
  cancel.textContent = "取消";
  cancel.addEventListener("click", () => {
    loadMessages();
  });

  panel.append(hint, cancel, confirm);
  article.append(panel);
  article.querySelector(".record-actions").remove();
}

async function loadMessages() {
  const response = await fetch("/api/messages");
  if (!response.ok) {
    showFeedback(await readError(response));
    status.textContent = "聊天记录加载失败。";
    return;
  }
  renderRecords(await response.json());
  status.textContent = "记录保存在当前服务的内存中。";
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    showFeedback("请输入要发送的内容。");
    return;
  }
  const response = await fetch("/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  });
  if (!response.ok) {
    showFeedback(await readError(response));
    return;
  }
  messageInput.value = "";
  showFeedback("已发送。");
  await loadMessages();
});

loadMessages();

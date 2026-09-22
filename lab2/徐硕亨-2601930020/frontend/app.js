document.addEventListener('DOMContentLoaded', () => {
    const convList = document.getElementById('conversations-list');
    const btnNewConv = document.getElementById('btn-new-conv');
    const currentConvTitle = document.getElementById('current-conv-title');
    const btnRenameConv = document.getElementById('btn-rename-conv');
    const btnDeleteConv = document.getElementById('btn-delete-conv');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const statusBanner = document.getElementById('status-banner');

    // 彈窗元件
    const editModal = document.getElementById('edit-modal');
    const modalTitle = document.getElementById('modal-title');
    const editInput = document.getElementById('edit-input');
    const btnSaveEdit = document.getElementById('btn-save-edit');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');

    let activeConvId = null;
    let modalMode = null; // 'rename_conv' 或 'edit_msg'
    let currentEditMsgId = null;

    function showStatus(text, isError = false) {
        if (!statusBanner) return;
        statusBanner.textContent = text;
        statusBanner.style.color = isError ? '#ef4444' : '#64748b';
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // 載入所有會話清單
    async function loadConversations(autoSelectId = null) {
        try {
            const res = await fetch('/api/conversations');
            if (!res.ok) throw new Error('獲取會話失敗');
            const list = await res.json();

            convList.innerHTML = '';
            list.forEach(c => {
                const item = document.createElement('div');
                item.className = `conv-item ${c.id === activeConvId ? 'active' : ''}`;
                item.setAttribute('data-id', c.id);
                item.innerHTML = `
                    <span class="conv-title">${escapeHtml(c.title)}</span>
                    <span class="conv-count">${c.message_count}</span>
                `;
                item.addEventListener('click', () => selectConversation(c.id));
                convList.appendChild(item);
            });

            // 若沒有選中的會話，選中第一個或指定會話
            if (!activeConvId && list.length > 0) {
                selectConversation(autoSelectId || list[0].id);
            } else if (autoSelectId) {
                selectConversation(autoSelectId);
            }
        } catch (err) {
            showStatus('無法讀取會話清單', true);
            console.error(err);
        }
    }

    // 選取特定會話
    async function selectConversation(id) {
        activeConvId = id;

        // 更新側邊欄樣式
        document.querySelectorAll('.conv-item').forEach(el => {
            if (parseInt(el.getAttribute('data-id'), 10) === id) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });

        try {
            showStatus('載入對話中...');
            const res = await fetch(`/api/conversations/${id}`);
            if (!res.ok) throw new Error('獲取對話詳情失敗');
            const conv = await res.json();

            currentConvTitle.textContent = conv.title;
            renderMessages(conv.messages || []);
            showStatus('已就緒（多會話上下文模式）');
        } catch (err) {
            showStatus('載入對話失敗', true);
            console.error(err);
        }
    }

    // 渲染對話訊息流
    function renderMessages(messages) {
        chatMessages.innerHTML = '';
        if (!messages || messages.length === 0) {
            chatMessages.innerHTML = '<div style="text-align:center; color:#94a3b8; margin-top:30px;">本會話尚無訊息，快來開始對話吧！</div>';
            return;
        }

        messages.forEach(m => {
            const item = document.createElement('div');
            item.className = `message-item ${m.role}`;
            item.setAttribute('data-id', m.id);

            item.innerHTML = `
                <div class="bubble">${escapeHtml(m.content)}</div>
                <div class="msg-actions">
                    <button class="btn-action edit" data-id="${m.id}">修改</button>
                    <button class="btn-action delete" data-id="${m.id}">刪除</button>
                </div>
            `;
            chatMessages.appendChild(item);
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 建立新會話
    btnNewConv.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            if (!res.ok) throw new Error('新建會話失敗');
            const newConv = await res.json();
            await loadConversations(newConv.id);
        } catch (err) {
            showStatus('新建會話失敗', true);
            console.error(err);
        }
    });

    // 重新命名會話
    btnRenameConv.addEventListener('click', () => {
        if (!activeConvId) return;
        modalMode = 'rename_conv';
        modalTitle.textContent = '重新命名會話';
        editInput.value = currentConvTitle.textContent;
        editModal.classList.remove('hidden');
        editInput.focus();
    });

    // 刪除會話
    btnDeleteConv.addEventListener('click', async () => {
        if (!activeConvId) return;
        try {
            const res = await fetch(`/api/conversations/${activeConvId}`, {
                method: 'DELETE'
            });
            if (!res.ok) throw new Error('刪除失敗');
            activeConvId = null;
            await loadConversations();
        } catch (err) {
            showStatus('刪除會話失敗', true);
            console.error(err);
        }
    });

    // 發送新問題（帶歷史上下文）
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = userInput.value.trim();
            if (!text || !activeConvId) return;

            userInput.value = '';
            showStatus('AI 思考中...');

            // 前端先即時上屏使用者輸入
            const tempUserMsg = document.createElement('div');
            tempUserMsg.className = 'message-item user';
            tempUserMsg.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
            chatMessages.appendChild(tempUserMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const res = await fetch(`/api/conversations/${activeConvId}/messages`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.error || '請求失敗');
                }

                const data = await res.json();
                renderMessages(data.conversation.messages);
                currentConvTitle.textContent = data.conversation.title;
                showStatus('已就緒（多會話上下文模式）');
                loadConversations(activeConvId); // 更新側邊欄標題與訊息數量
            } catch (err) {
                showStatus(`發送失敗: ${err.message}`, true);
                console.error(err);
            }
        });
    }

    // 訊息修改/刪除點擊事件
    chatMessages.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.edit');
        const deleteBtn = e.target.closest('.delete');

        if (editBtn) {
            const mid = parseInt(editBtn.getAttribute('data-id'), 10);
            const msgItem = editBtn.closest('.message-item');
            const bubbleText = msgItem.querySelector('.bubble').textContent;

            modalMode = 'edit_msg';
            currentEditMsgId = mid;
            modalTitle.textContent = '修改訊息內容';
            editInput.value = bubbleText;
            editModal.classList.remove('hidden');
            editInput.focus();
        }

        if (deleteBtn) {
            const mid = parseInt(deleteBtn.getAttribute('data-id'), 10);
            try {
                const res = await fetch(`/api/conversations/${activeConvId}/messages/${mid}`, {
                    method: 'DELETE'
                });
                if (!res.ok) throw new Error('刪除訊息失敗');
                await selectConversation(activeConvId);
                loadConversations(activeConvId);
            } catch (err) {
                showStatus('刪除訊息失敗', true);
                console.error(err);
            }
        }
    });

    // 彈窗保存
    if (btnSaveEdit) {
        btnSaveEdit.addEventListener('click', async () => {
            const newVal = editInput.value.trim();
            if (!newVal) return;

            if (modalMode === 'rename_conv') {
                try {
                    const res = await fetch(`/api/conversations/${activeConvId}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title: newVal })
                    });
                    if (!res.ok) throw new Error('修改標題失敗');
                    editModal.classList.add('hidden');
                    loadConversations(activeConvId);
                } catch (err) {
                    showStatus('重命名失敗', true);
                    console.error(err);
                }
            } else if (modalMode === 'edit_msg') {
                try {
                    const res = await fetch(`/api/conversations/${activeConvId}/messages/${currentEditMsgId}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content: newVal })
                    });
                    if (!res.ok) throw new Error('修改訊息失敗');
                    editModal.classList.add('hidden');
                    currentEditMsgId = null;
                    await selectConversation(activeConvId);
                } catch (err) {
                    showStatus('修改訊息失敗', true);
                    console.error(err);
                }
            }
        });
    }

    // 彈窗取消
    if (btnCancelEdit) {
        btnCancelEdit.addEventListener('click', () => {
            editModal.classList.add('hidden');
            modalMode = null;
            currentEditMsgId = null;
        });
    }

    // 初始載入
    loadConversations();
});

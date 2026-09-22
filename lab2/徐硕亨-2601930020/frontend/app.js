document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const statusBanner = document.getElementById('status-banner');

    // 頁面內修改彈窗元件
    const editModal = document.getElementById('edit-modal');
    const editInput = document.getElementById('edit-input');
    const btnSaveEdit = document.getElementById('btn-save-edit');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    let currentEditId = null;

    // 顯示頁面內狀態提示（不使用原生 alert）
    function showStatus(text, isError = false) {
        if (!statusBanner) return;
        statusBanner.textContent = text;
        statusBanner.style.background = isError ? 'rgba(239, 68, 68, 0.4)' : 'rgba(255, 255, 255, 0.2)';
    }

    // 渲染所有訊息卡片
    function renderMessages(messages) {
        chatMessages.innerHTML = '';
        if (!messages || messages.length === 0) {
            chatMessages.innerHTML = '<div style="text-align:center; color:#94a3b8; margin-top:20px;">目前尚無對話記錄，請在下方輸入發送！</div>';
            return;
        }

        messages.forEach(msg => {
            const card = document.createElement('div');
            card.className = 'message-card';
            card.setAttribute('data-id', msg.id);

            card.innerHTML = `
                <div class="message-bubble user-bubble">
                    <span class="sender-label">用戶：</span>
                    <span class="message-text">${escapeHtml(msg.message)}</span>
                </div>
                <div class="message-bubble bot-bubble">
                    <span class="sender-label">AI：</span>
                    <span class="reply-text">${escapeHtml(msg.reply)}</span>
                </div>
                <div class="card-actions">
                    <button class="btn-action btn-edit" data-id="${msg.id}">修改</button>
                    <button class="btn-action btn-delete" data-id="${msg.id}">刪除</button>
                </div>
            `;
            chatMessages.appendChild(card);
        });

        // 捲動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 防範 XSS 轉義工具函式
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // 1. 取得所有訊息 (GET /api/messages)
    async function loadMessages() {
        try {
            const res = await fetch('/api/messages');
            if (!res.ok) throw new Error('獲取對話失敗');
            const data = await res.json();
            renderMessages(data);
            showStatus('前後端已接通（記憶體儲存模式）');
        } catch (err) {
            showStatus('無法連接後端服務', true);
            console.error(err);
        }
    }

    // 2. 發送新訊息 (POST /api/messages)
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = userInput.value.trim();
            if (!text) return;

            userInput.value = '';
            showStatus('發送中...');

            try {
                const res = await fetch('/api/messages', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                if (!res.ok) throw new Error('發送失敗');
                await loadMessages(); // 重新載入最新對話
                showStatus('前後端已接通（記憶體儲存模式）');
            } catch (err) {
                showStatus('發送訊息失敗，請檢查後端', true);
                console.error(err);
            }
        });
    }

    // 卡片內「修改」與「刪除」事件委託
    chatMessages.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.btn-edit');
        const deleteBtn = e.target.closest('.btn-delete');

        if (editBtn) {
            const id = parseInt(editBtn.getAttribute('data-id'), 10);
            const card = editBtn.closest('.message-card');
            const currentText = card.querySelector('.message-text').textContent;

            currentEditId = id;
            editInput.value = currentText;
            editModal.classList.remove('hidden');
            editInput.focus();
        }

        if (deleteBtn) {
            const id = parseInt(deleteBtn.getAttribute('data-id'), 10);
            try {
                const res = await fetch(`/api/messages/${id}`, {
                    method: 'DELETE'
                });
                if (!res.ok) throw new Error('刪除失敗');
                await loadMessages();
            } catch (err) {
                showStatus('刪除失敗', true);
                console.error(err);
            }
        }
    });

    // 保存修改 (PATCH /api/messages/<id>)
    if (btnSaveEdit) {
        btnSaveEdit.addEventListener('click', async () => {
            if (!currentEditId) return;
            const updatedText = editInput.value.trim();
            if (!updatedText) return;

            try {
                const res = await fetch(`/api/messages/${currentEditId}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: updatedText })
                });
                if (!res.ok) throw new Error('更新失敗');
                editModal.classList.add('hidden');
                currentEditId = null;
                await loadMessages();
            } catch (err) {
                showStatus('更新訊息失敗', true);
                console.error(err);
            }
        });
    }

    // 取消修改
    if (btnCancelEdit) {
        btnCancelEdit.addEventListener('click', () => {
            editModal.classList.add('hidden');
            currentEditId = null;
        });
    }

    // 頁面初次載入
    loadMessages();
});

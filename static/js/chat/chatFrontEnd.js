document.addEventListener("DOMContentLoaded", function () {
    (async function () {
        try {
            const response = await fetch("/chat/chat-config/");
            if (!response.ok) throw new Error("Failed to load chat config");

            const config = await response.json();

            const {
                adminAvatarUrl,
                defaultAvatarUrl,
                userId,
                wsProtocol,
                host,
                apiMessagesUrl,
                userIsChatBanned,
                userIsStaffOrSuperuser
            } = config;

            if (!userId) return;

            const chatToggleBtn = document.getElementById('chat-toggle');
            const chatBox = document.getElementById('chat-box');
            const chatCloseBtn = document.getElementById('chat-close');
            const chatMessages = document.getElementById('chat-messages');
            const chatForm = document.getElementById('chat-form');
            const chatInput = document.getElementById('chat-input');

            let chatSocket = null;
            const recentMessagesSet = new Set();

            function showBanNotice() {
                if (document.querySelector('.ban-notice'))
                    return;
                const banNotice = document.createElement('div');
                banNotice.className = 'ban-notice fixed top-6 right-6 max-w-sm bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded-lg shadow-lg z-50 flex justify-between items-start';
                banNotice.innerHTML = `
                    <div>
                        <strong class="block font-semibold mb-1">Chat Unavailable</strong>
                        <span>You are currently banned from using the chat feature.</span>
                    </div>
                    <button
                        aria-label="Close"
                        class="ml-4 text-red-800 hover:text-red-900 font-bold"
                        style="background: none; border: none; font-size: 1.25rem; line-height: 1; cursor: pointer;"
                    >&times;</button>
                `;

                const closeBtn = banNotice.querySelector('button');
                closeBtn.addEventListener('click', () => {
                    banNotice.remove();
                });

                document.body.appendChild(banNotice);
                setTimeout(() => banNotice.remove(), 6000);
            }


            if (chatToggleBtn) {
                chatToggleBtn.addEventListener('click', () => {
                    if (userIsStaffOrSuperuser) {
                        window.location.href = "/chat/admin";
                        return;
                    }

                    if (userIsChatBanned) {
                        showBanNotice();
                        return;
                    }

                    if (chatBox.classList.contains('invisible')) {
                        chatBox.classList.remove('invisible', 'opacity-0');
                        chatBox.classList.add('opacity-100');
                        chatInput.focus();
                        loadChatMessages();
                        connectSocket();
                    } else {
                        chatBox.classList.add('opacity-0', 'invisible');
                    }
                });
            }

            if (chatCloseBtn) {
                chatCloseBtn.addEventListener('click', () => {
                    chatBox.classList.add('opacity-0', 'invisible');
                });
            }

            function messageKey(msg) {
                return `${msg.timestamp}|${msg.sender_id}|${msg.text}`;
            }

            function addMessageSafe(msg) {
                const key = messageKey(msg);
                if (recentMessagesSet.has(key)) return;
                recentMessagesSet.add(key);
                if (recentMessagesSet.size > 500) {
                    const keys = Array.from(recentMessagesSet).slice(-250);
                    recentMessagesSet.clear();
                    keys.forEach(k => recentMessagesSet.add(k));
                }
                addMessage(msg);
            }

            function addMessage({text, avatarUrl, timestamp, fromAdmin}) {
                const container = document.createElement('div');
                container.className = `flex ${fromAdmin ? 'justify-end' : 'justify-start'} mb-3`;

                const contentRow = document.createElement('div');
                contentRow.className = `flex items-center space-x-2 ${fromAdmin ? 'flex-row-reverse space-x-reverse' : ''}`;

                const avatar = document.createElement('img');
                avatar.src = avatarUrl || defaultAvatarUrl;
                avatar.alt = 'avatar';
                avatar.className = 'w-8 h-8 rounded-full object-cover';

                const messageAndTimestamp = document.createElement('div');
                messageAndTimestamp.className = 'flex flex-col';

                const message = document.createElement('div');
                message.className = `px-4 py-2 rounded-lg text-sm break-words max-w-xs ${fromAdmin ? 'bg-gray-200 text-gray-900 rounded-br-none' : 'bg-blue-500 text-white rounded-bl-none'}`;
                message.textContent = text;

                const time = document.createElement('span');
                time.className = `text-xs text-gray-400 mt-1 ${fromAdmin ? 'text-right' : 'text-left'}`;
                time.textContent = timestamp ? new Date(timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                }) : '';

                messageAndTimestamp.appendChild(message);
                messageAndTimestamp.appendChild(time);

                contentRow.appendChild(avatar);
                contentRow.appendChild(messageAndTimestamp);

                container.appendChild(contentRow);
                chatMessages.appendChild(container);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function clearChat() {
                chatMessages.innerHTML = '';
                recentMessagesSet.clear();
            }

            async function loadChatMessages() {
                clearChat();
                if (!apiMessagesUrl) return;

                try {
                    const res = await fetch(apiMessagesUrl);
                    if (!res.ok) throw new Error('Failed to fetch messages');
                    const data = await res.json();
                    const recentMessages = data.messages.slice(-100);
                    recentMessages.forEach(msg => {
                        addMessageSafe({
                            text: msg.message,
                            username: msg.sender_username || 'You',
                            avatarUrl: msg.from_admin ? adminAvatarUrl : (msg.avatar_url || defaultAvatarUrl),
                            timestamp: msg.timestamp,
                            fromAdmin: msg.from_admin,
                            sender_id: msg.sender_id,
                        });
                    });
                } catch (err) {
                    console.error('Error loading messages:', err);
                    chatMessages.innerHTML = '<div class="text-center text-red-500">Failed to load messages.</div>';
                }
            }

            function connectSocket() {
                if (chatSocket) chatSocket.close();

                const socketUrl = `${wsProtocol}://${host}/ws/chat/user/${userId}/`;
                chatSocket = new WebSocket(socketUrl);

                chatSocket.onopen = () => {
                    chatInput.disabled = false;
                    chatForm.querySelector('button[type="submit"]').disabled = false;
                };

                chatSocket.onmessage = (e) => {
                    const data = JSON.parse(e.data);
                    addMessageSafe({
                        text: data.message,
                        username: data.username || (data.from_admin ? 'Admin' : 'You'),
                        avatarUrl: data.from_admin ? adminAvatarUrl : (data.avatar_url || defaultAvatarUrl),
                        timestamp: data.timestamp,
                        fromAdmin: data.from_admin,
                        sender_id: data.sender_id,
                    });
                };

                chatSocket.onclose = () => {
                    chatInput.disabled = true;
                    chatForm.querySelector('button[type="submit"]').disabled = true;
                };

                chatSocket.onerror = (err) => console.error('WebSocket error:', err);
            }

            if (chatForm) {
                chatForm.addEventListener('submit', function (e) {
                    e.preventDefault();
                    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;
                    const message = chatInput.value.trim();
                    if (!message) return;
                    chatSocket.send(JSON.stringify({message}));
                    chatInput.value = '';
                });
            }

        } catch (err) {
            console.error("Chat config load failed:", err);
        }
    })();
});

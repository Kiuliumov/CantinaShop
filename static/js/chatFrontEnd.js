(function () {
  let chatSocket = null;
  let chatMessages, chatForm, chatInput, chatToggleBtn, chatBox;

  let currentUserId = window.currentUserId || null;

  function init() {
    chatMessages = document.getElementById('chat-messages');
    chatForm = document.getElementById('chat-form');
    chatInput = document.getElementById('chat-input');
    chatToggleBtn = document.getElementById('chat-toggle');
    chatBox = document.getElementById('chat-box');

    if (!currentUserId || !chatMessages || !chatForm || !chatInput) {
      console.error("Chat initialization failed: missing elements or user ID");
      return;
    }

    chatForm.addEventListener('submit', onSendMessage);
    chatToggleBtn?.addEventListener('click', toggleChat);
    document.getElementById('chat-close')?.addEventListener('click', toggleChat);

    loadChatMessages(currentUserId);
    connectSocket(currentUserId);
  }

  function toggleChat() {
    if (!chatBox) return;

    if (userIsStaffOrSuperuser) {
      window.location.href = `chat/admin`;
    }

    const isOpen = chatBox.classList.contains('opacity-100');
    if (isOpen) {
      chatBox.classList.remove('opacity-100', 'visible');
      chatBox.classList.add('opacity-0', 'invisible');
    } else {
      chatBox.classList.remove('opacity-0', 'invisible');
      chatBox.classList.add('opacity-100', 'visible');
    }
  }

  function clearChat() {
    chatMessages.innerHTML = '';
  }

  async function loadChatMessages(userId) {
    clearChat();
    try {
      const res = await fetch(`/chat/messages/${userId}/`);
      console.log(`/chat/messages/${userId}/`)
      if (!res.ok) throw new Error('Failed to fetch messages');
      const data = await res.json();

      const recentMessages = data.messages.slice(-100);
      recentMessages.forEach(msg => {
        addMessage({
          text: msg.message,
          username: msg.sender_username,
          avatarUrl: (msg.sender_id === 0 || msg.from_admin) ? '/static/images/admin.jpg' : (msg.avatar_url || '/static/images/avatar.png'),
          timestamp: msg.timestamp,
          fromAdmin: msg.sender_id === 0 || msg.from_admin,
        });
      });
    } catch (err) {
      console.error(err);
    }
  }

  function connectSocket(userId) {
    if (chatSocket) chatSocket.close();

    const socketUrl =
      (window.location.protocol === "https:" ? "wss://" : "ws://") +
      window.location.host +
      `/ws/chat/user/${userId}/`;

    chatSocket = new WebSocket(socketUrl);

    chatSocket.onopen = () => {
      chatInput.disabled = false;
      const submitBtn = chatForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = false;
    };

    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      addMessage({
        text: data.message,
        username: data.username,
        avatarUrl: data.avatar_url || '/static/images/avatar.png',
        timestamp: data.timestamp,
        fromAdmin: data.from_admin,
      });
    };

    chatSocket.onclose = () => {
      chatInput.disabled = true;
      const submitBtn = chatForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
    };
  }

  function addMessage({ text, username, avatarUrl, timestamp, fromAdmin }) {
    const bubble = document.createElement('div');
    bubble.className = 'flex flex-col space-y-1 max-w-xs ' + (fromAdmin ? 'mr-auto items-start' : 'ml-auto items-end');

    const bubbleRow = document.createElement('div');
    bubbleRow.className = 'flex items-start space-x-2';

    const avatar = document.createElement('img');
    avatar.src = avatarUrl;
    avatar.alt = username;
    avatar.className = 'w-8 h-8 rounded-full object-cover';

    const msgDiv = document.createElement('div');
    msgDiv.className = fromAdmin
      ? 'bg-indigo-600 text-white px-3 py-2 rounded-lg'
      : 'bg-gray-700 text-gray-100 px-3 py-2 rounded-lg';
    msgDiv.textContent = text;

    if (fromAdmin) {
      bubbleRow.appendChild(avatar);
      bubbleRow.appendChild(msgDiv);
    } else {
      bubbleRow.appendChild(msgDiv);
      bubbleRow.appendChild(avatar);
    }

    const timeDiv = document.createElement('div');
    timeDiv.className = 'text-xs text-gray-400';
    timeDiv.textContent = timestamp
      ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : '';

    bubble.appendChild(bubbleRow);
    bubble.appendChild(timeDiv);

    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function onSendMessage(e) {
    e.preventDefault();
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;

    const message = chatInput.value.trim();
    if (!message) return;

    chatSocket.send(JSON.stringify({ message }));
    chatInput.value = '';
  }

  window.chatApp = { init };
})();

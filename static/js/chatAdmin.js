(function () {
  let adminAvatarUrl = window.chatConfig?.adminAvatarUrl || '/static/images/admin.jpg';
  let defaultAvatarUrl = window.chatConfig?.defaultAvatarUrl || '/static/images/avatar.png';
  let messagesApiUrlBase = window.chatConfig?.messagesApiUrlBase || '/chat/messages/';
  let websocketBaseUrl = window.chatConfig?.websocketBaseUrl || (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;

  let currentChatUserId = null;
  let chatSocket = null;

  let chatHeader, userList, chatMessages, chatForm, chatInput, userSearchInput;

  const recentMessagesSet = new Set();

  function init() {
    chatHeader = document.getElementById('chat-header');
    userList = document.getElementById('user-list');
    chatMessages = document.getElementById('chat-messages');
    chatForm = document.getElementById('chat-form');
    chatInput = document.getElementById('chat-input');
    userSearchInput = document.getElementById('user-search');

    userSearchInput.addEventListener('input', onUserSearch);
    userList.addEventListener('click', onUserSelect);
    chatForm.addEventListener('submit', onSendMessage);

    chatInput.disabled = true;
    chatForm.querySelector('button[type="submit"]').disabled = true;
  }

  function onUserSearch() {
    const query = userSearchInput.value.toLowerCase();
    const userButtons = userList.querySelectorAll('button[data-username]');
    userButtons.forEach(btn => {
      const username = btn.getAttribute('data-username').toLowerCase();
      btn.parentElement.style.display = username.includes(query) ? '' : 'none';
    });
  }

  function clearChat() {
    chatMessages.innerHTML = '';
    recentMessagesSet.clear();
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

  function addMessage({ text, username, avatarUrl, timestamp, fromAdmin }) {
    const bubble = document.createElement('div');
    bubble.className = 'flex flex-col space-y-1 max-w-xs ' + (fromAdmin ? 'mr-auto items-start' : 'ml-auto items-end');

    const bubbleRow = document.createElement('div');
    bubbleRow.className = 'flex items-start space-x-2';

    const avatar = document.createElement('img');
    avatar.src = avatarUrl || defaultAvatarUrl;
    avatar.alt = username;
    avatar.className = 'w-8 h-8 rounded-full object-cover';

    const msgDiv = document.createElement('div');
    msgDiv.className = fromAdmin
      ? 'bg-indigo-600 text-white px-3 py-2 rounded-lg break-words'
      : 'bg-gray-700 text-gray-100 px-3 py-2 rounded-lg break-words';
    msgDiv.style.wordBreak = 'break-word';
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

  async function loadChatMessages(userId) {
    clearChat();
    try {
      const url = messagesApiUrlBase + userId + '/';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch messages');
      const data = await res.json();
      const recentMessages = data.messages.slice(-100);
      recentMessages.forEach(msg => {
        addMessageSafe({
          text: msg.message,
          username: msg.sender_username,
          avatarUrl: (msg.sender_id === 0 || msg.from_admin) ? adminAvatarUrl : (msg.avatar_url || defaultAvatarUrl),
          timestamp: msg.timestamp,
          fromAdmin: msg.sender_id === 0 || msg.from_admin,
          sender_id: msg.sender_id,
        });
      });
    } catch (err) {
      console.error(err);
    }
  }

  function connectSocket(userId) {
    if (chatSocket) {
      chatSocket.close();
    }

    chatSocket = new WebSocket(
      `${websocketBaseUrl}/ws/chat/admin/${userId}/`
    );

    chatSocket.onopen = () => {
      chatInput.disabled = false;
      chatForm.querySelector('button[type="submit"]').disabled = false;
    };

    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const fromAdmin = data.from_admin;
      const senderId = data.sender_id;

      if (parseInt(senderId) !== parseInt(currentChatUserId) && !fromAdmin) {
        return;
      }

      addMessageSafe({
        text: data.message,
        username: data.username || 'Admin',
        avatarUrl: fromAdmin ? adminAvatarUrl : (data.avatar_url || defaultAvatarUrl),
        timestamp: data.timestamp,
        fromAdmin: fromAdmin,
        sender_id: senderId,
      });
    };

    chatSocket.onclose = () => {
      chatInput.disabled = true;
      chatForm.querySelector('button[type="submit"]').disabled = true;
    };
  }

  function onUserSelect(e) {
    const btn = e.target.closest('button[data-user-id]');
    if (!btn) return;

    currentChatUserId = btn.getAttribute('data-user-id');
    const username = btn.getAttribute('data-username');

    chatHeader.textContent = `Chat with ${username}`;
    chatInput.value = '';
    chatInput.focus();

    loadChatMessages(currentChatUserId);
    connectSocket(currentChatUserId);
  }

  function onSendMessage(e) {
    e.preventDefault();
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;

    const message = chatInput.value.trim();
    if (!message) return;

    chatSocket.send(JSON.stringify({ message }));
    chatInput.value = '';
  }

  window.chatApp = {
    init,
  };
})();

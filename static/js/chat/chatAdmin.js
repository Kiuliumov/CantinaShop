(async function () {
  let adminAvatarUrl = '/static/images/admin.jpg';
  let defaultAvatarUrl = '/static/images/avatar.png';
  let messagesApiUrlBase = '/api/messages/';
  let websocketBaseUrl = (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;

  try {
    const res = await fetch('/chat/chat-config/');
    if (res.ok) {
      const config = await res.json();
      adminAvatarUrl = config.adminAvatarUrl || adminAvatarUrl;
      defaultAvatarUrl = config.defaultAvatarUrl || defaultAvatarUrl;
      messagesApiUrlBase = config.apiMessagesUrl.replace(/\/\d+\/?$/, '/');
      const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
      const host = config.host || window.location.host;
      websocketBaseUrl = `${wsProtocol}://${host}`;
    }
  } catch {}

  let currentChatUserId = null;
  let chatSocket = null;
  let chatHeader, userList, chatMessages, chatForm, chatInput, userSearchInput;
  const recentMessagesSet = new Set();
  const unreadCounts = new Map();

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

    loadUnreadCountsFromDOM();

    const firstUserBtn = userList.querySelector('button[data-user-id]');
    if (firstUserBtn) {
      firstUserBtn.click();
    }
  }

  function loadUnreadCountsFromDOM() {
    unreadCounts.clear();
    const buttons = userList.querySelectorAll('button[data-user-id]');
    buttons.forEach(btn => {
      const badge = btn.querySelector('.unread-badge');
      if (badge && !badge.classList.contains('hidden')) {
        const userId = btn.getAttribute('data-user-id');
        let countText = badge.textContent.trim();
        let count = countText === '9+' ? 9 : parseInt(countText) || 0;
        unreadCounts.set(userId, count);
      }
    });
  }

  function updateUnreadBadge(userId, count) {
  const btn = userList.querySelector(`button[data-user-id="${userId}"]`);
  if (!btn) return;

  let badge = btn.querySelector('.unread-badge');

  if (count > 0) {
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'unread-badge flex items-center justify-center';
      badge.style.position = 'absolute';
      badge.style.top = '6px';
      badge.style.right = '6px';
      badge.style.width = '1.25rem';
      badge.style.height = '1.25rem';
      badge.style.fontSize = '0.75rem';
      badge.style.lineHeight = '1.25rem';
      badge.style.borderRadius = '9999px';
      badge.style.backgroundColor = '#dc2626';
      badge.style.color = 'white';
      btn.style.position = 'relative';
      btn.appendChild(badge);
    }
    badge.textContent = count > 9 ? '9+' : count;
    badge.classList.remove('hidden');
  } else {
    if (badge) {
      badge.remove();
    }
  }
}


  function clearUnread(userId) {
    unreadCounts.set(userId, 0);
    updateUnreadBadge(userId, 0);
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
    msgDiv.className = (fromAdmin
      ? 'bg-indigo-600 text-white'
      : 'bg-gray-700 text-gray-100') + ' px-3 py-2 rounded-lg break-words';
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

  function moveUserToTop(userId) {
    const btn = userList.querySelector(`button[data-user-id="${userId}"]`);
    if (!btn) return;
    const li = btn.parentElement;
    const ul = li.parentElement;
    ul.prepend(li);
  }

  async function loadChatMessages(userId) {
    clearChat();
    try {
      const url = `${messagesApiUrlBase}${userId}/?limit=100`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch messages');
      const data = await res.json();
      data.messages.forEach(msg => {
        addMessageSafe({
          text: msg.message,
          username: msg.sender_username,
          avatarUrl: (msg.sender_id === 0 || msg.from_admin) ? adminAvatarUrl : (msg.avatar_url || defaultAvatarUrl),
          timestamp: msg.timestamp,
          fromAdmin: msg.sender_id === 0 || msg.from_admin,
          sender_id: msg.sender_id.toString(),
        });
      });
      clearUnread(userId);
      await markMessagesRead(userId);
      moveUserToTop(userId);
    } catch (err) {
      console.error(err);
    }
  }

  async function markMessagesRead(userId) {
    try {
      await fetch(`/chat/mark-read/${userId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
      });
    } catch {}
  }

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        return decodeURIComponent(cookie.slice(name.length + 1));
      }
    }
    return null;
  }

  function connectSocket(userId) {
    if (chatSocket) chatSocket.close();

    chatSocket = new WebSocket(`${websocketBaseUrl}/ws/chat/admin/${userId}/`);

    chatSocket.onopen = () => {
      chatInput.disabled = false;
      chatForm.querySelector('button[type="submit"]').disabled = false;
    };

    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const fromAdmin = data.from_admin;
      const senderId = data.sender_id.toString();

      if (fromAdmin) {
        if (senderId === currentChatUserId) {
          addMessageSafe({
            text: data.message,
            username: 'Admin',
            avatarUrl: adminAvatarUrl,
            timestamp: data.timestamp,
            fromAdmin: true,
            sender_id: senderId,
          });
        }
        moveUserToTop(senderId);
        return;
      }

      if (senderId === currentChatUserId) {
        addMessageSafe({
          text: data.message,
          username: data.username || 'User',
          avatarUrl: data.avatar_url || defaultAvatarUrl,
          timestamp: data.timestamp,
          fromAdmin: false,
          sender_id: senderId,
        });
        clearUnread(senderId);
        markMessagesRead(senderId);
      } else {
        const count = (unreadCounts.get(senderId) || 0) + 1;
        unreadCounts.set(senderId, count);
        updateUnreadBadge(senderId, count);
      }
      moveUserToTop(senderId);
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
    clearUnread(currentChatUserId);
    loadChatMessages(currentChatUserId);
    connectSocket(currentChatUserId);
  }

  function onSendMessage(e) {
    e.preventDefault();
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;
    const message = chatInput.value.trim();
    if (!message) return;
    addMessageSafe({
      text: message,
      username: 'Admin',
      avatarUrl: adminAvatarUrl,
      timestamp: new Date().toISOString(),
      fromAdmin: true,
      sender_id: '0',
    });
    chatSocket.send(JSON.stringify({ message }));
    chatInput.value = '';
    moveUserToTop(currentChatUserId);
  }

  window.chatApp = { init };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

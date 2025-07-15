const chatToggle = document.getElementById('chat-toggle');
const chatBox = document.getElementById('chat-box');
const chatClose = document.getElementById('chat-close');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');

const adminAvatarUrl = "/static/images/admin.jpg";
const defaultAvatarUrl = "/static/images/avatar.png";

// You need to set currentUsername & currentChatUserId somehow, e.g. from your Django template context or user action
// Example (replace these with your actual values):
const currentUsername = "{{ request.user.username }}";  // Django template variable
let currentChatUserId = null;  // Will be set when user selects a chat partner

// Clear chat messages UI
function clearChat() {
  chatMessages.innerHTML = '';
}

// Load chat messages from backend API for given userId
function loadChatMessages(userId) {
  clearChat();
  if (!userId) return;

  fetch(`/chat/messages/${userId}/`)
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch messages');
      return res.json();
    })
    .then(data => {
      data.messages.forEach(msg => {
        const isFromCurrentUser = (msg.sender_username === currentUsername);
        if (isFromCurrentUser) {
          addUserMessage(msg.message, msg.avatar_url || defaultAvatarUrl, msg.timestamp);
        } else {
          addAdminMessage(msg.message, msg.avatar_url || adminAvatarUrl, msg.timestamp);
        }
      });
    })
    .catch(err => {
      console.error('Error loading messages:', err);
    });
}

// When you open chat with user (replace this with your own UI event)
function openChatWithUser(userId, username) {
  currentChatUserId = userId;
  clearChat();
  loadChatMessages(userId);
  chatInput.disabled = false;
  chatForm.querySelector('button[type="submit"]').disabled = false;
  chatInput.focus();
  // Update chat header, etc.
}

// Send message handler
chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  if (!currentChatUserId) return; // no user selected

  const message = chatInput.value.trim();
  if (!message) return;
  const timestamp = new Date().toISOString();

  // Send message over WebSocket
  chatSocket.send(JSON.stringify({
    'message': message,
    'recipient_id': currentChatUserId,  // send recipient info for backend to handle
  }));

  // Optimistically add user message to UI
  addUserMessage(message, defaultAvatarUrl, timestamp);
  chatInput.value = '';
});

// Your existing addUserMessage and addAdminMessage functions remain the same

// WebSocket message handler — when message received, append it to chat UI
chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data.message;
  const username = data.username;
  const timestamp = data.timestamp || new Date().toISOString();

  if (username === currentUsername) {
    addUserMessage(message, data.avatar_url || defaultAvatarUrl, timestamp);
  } else {
    addAdminMessage(message, data.avatar_url || adminAvatarUrl, timestamp);
  }
};

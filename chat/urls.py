from django.urls import path
from chat.views import AdminChatHubView, ChatFrontendConfigAPIView, MarkMessagesReadView, ChatMessagesAPIView
urlpatterns = [
    path('admin/', AdminChatHubView.as_view(), name='admin_chat_hub'),
    path('messages/<int:user_id>/', ChatMessagesAPIView.as_view(), name='chat-messages-api-base'),
    path('chat-config/', ChatFrontendConfigAPIView.as_view(), name='chat-config'),
    path('mark-read/<int:user_id>/', MarkMessagesReadView.as_view(), name='mark-messages-read'),
]
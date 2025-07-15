from django.urls import path

from chat.views import AdminChatHubView, ChatMessagesView

urlpatterns = [
    path('admin/', AdminChatHubView.as_view(), name='admin_chat_hub'),
    path('messages/<int:user_id>/', ChatMessagesView.as_view(), name='chat_messages'),
]
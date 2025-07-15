from django.urls import path

from chat.views import AdminChatHubView, ChatMessagesAPIView

urlpatterns = [
    path('admin/', AdminChatHubView.as_view(), name='admin_chat_hub'),
    path('messages/<int:user_id>/', ChatMessagesAPIView.as_view(), name='chat_messages'),
]
from django.urls import path

from chat import routing
from chat.api.views import ChatMessagesAPIView
from chat.views import AdminChatHubView

urlpatterns = [
    path('admin/', AdminChatHubView.as_view(), name='admin_chat_hub'),
    path('messages/<int:user_id>/', ChatMessagesAPIView.as_view(), name='chat-messages-api-base'),
]
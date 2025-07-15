from django.urls import path

from chat.views import RecentChatMessagesView

urlpatterns = [
    path('recent/', RecentChatMessagesView.as_view(), name='recent_chat_messages'),
]
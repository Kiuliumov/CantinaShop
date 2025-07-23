from django.urls import path
from chat.views import AdminChatHubView

urlpatterns = [
    path('admin/', AdminChatHubView.as_view(), name='admin_chat_hub'),
]
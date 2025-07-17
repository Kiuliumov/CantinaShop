from django.urls import path
from api.views import ChatMessagesAPIView


urlpatterns = [
    path('messages/<int:user_id>/', ChatMessagesAPIView.as_view(), name='chat-messages-api-base'),

]
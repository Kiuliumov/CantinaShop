from django.urls import re_path
from chat.consumers import AdminConsumer, UserConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/user/(?P<user_id>\d+)/$', UserConsumer.as_asgi(), name='chat-ws-user'),
    re_path(r'ws/chat/admin/(?P<user_id>\d+)/$', AdminConsumer.as_asgi(), name='chat-ws-admin'),
]

from django.urls import re_path
from chat.consumers import BaseChatConsumer, AdminConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/user/(?P<user_id>\d+)/$', BaseChatConsumer.as_asgi()),
    re_path(r'ws/chat/admin/(?P<user_id>\d+)/$', AdminConsumer.as_asgi()),

]

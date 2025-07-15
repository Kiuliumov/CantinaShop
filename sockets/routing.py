from django.urls import re_path
from sockets.consumers import TestConsumer, ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/test/$', TestConsumer.as_asgi()),
    re_path(r'^ws/chat/$', ChatConsumer.as_asgi()),

]

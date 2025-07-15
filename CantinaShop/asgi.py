import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import sockets.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CantinaShop.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            sockets.routing.websocket_urlpatterns
        )
    ),
})

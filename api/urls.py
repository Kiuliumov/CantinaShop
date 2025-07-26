from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from api.views import ChatMessagesAPIView, ProductListCreateAPIView
drf_spectacular = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
urlpatterns = [
    path('messages/<int:user_id>/', ChatMessagesAPIView.as_view(), name='chat-messages-api-base'),
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-api-base'),
] + drf_spectacular
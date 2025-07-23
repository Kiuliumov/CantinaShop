from django.urls import path
from api.views import ChatMessagesAPIView, ProductListAPIView


urlpatterns = [
    path('messages/<int:user_id>/', ChatMessagesAPIView.as_view(), name='chat-messages-api-base'),
    path('products/', ProductListAPIView.as_view(), name='product-list-api-base'),
]
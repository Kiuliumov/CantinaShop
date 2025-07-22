from django.urls import path

from orders.views import AddToCartView

urlpatterns = [
    path("add-to-cart/<slug:slug>/", AddToCartView.as_view(), name="cart_save"),
]
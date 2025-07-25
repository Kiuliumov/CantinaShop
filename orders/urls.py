from django.urls import path

from orders.views import AddToCartView, CheckoutView

urlpatterns = [
    path("add-to-cart/<slug:slug>/", AddToCartView.as_view(), name="cart_save"),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]
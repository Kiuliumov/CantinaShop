from django.urls import path

from orders.views import AddToCartView, CheckoutView, OrderCreateView

urlpatterns = [
    path("add-to-cart/<slug:slug>/", AddToCartView.as_view(), name="cart_save"),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/place-order/', OrderCreateView.as_view(), name='order'),
]
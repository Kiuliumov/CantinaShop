import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product

# Create your views here.
class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        try:
            quantity = int(request.GET.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        cart_cookie = request.COOKIES.get('cart')
        try:
            raw_cart = json.loads(cart_cookie) if cart_cookie else []
        except json.JSONDecodeError:
            raw_cart = []

        cart = []
        for item in raw_cart:
            if isinstance(item, str):
                cart.append({'slug': item, 'quantity': 1})
            elif isinstance(item, dict):
                cart.append(item)

        product_in_cart = next((item for item in cart if item['slug'] == slug), None)

        if product_in_cart:
            product_in_cart['quantity'] += quantity
        else:
            cart.append({'slug': slug, 'quantity': quantity})

        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(
            'cart',
            json.dumps(cart),
            max_age=60 * 60 * 24 * 7,
            httponly=True,
            samesite='Lax',
        )
        return response
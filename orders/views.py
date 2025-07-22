import json

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View

from products.models import Product


# Create your views here.

class AddToCartView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        cart_cookie = request.COOKIES.get('cart')
        try:
            cart = json.loads(cart_cookie) if cart_cookie else []
        except json.JSONDecodeError:
            cart = []

        if slug not in cart:
            cart.append(slug)

        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(
            'cart',
            json.dumps(cart),
            max_age=60 * 60 * 24 * 7,
            httponly=True,
            samesite='Lax',
        )
        return response

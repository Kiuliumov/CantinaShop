import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from products.models import Product


# Create your views here.

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json

class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        cart_cookie = request.COOKIES.get('cart')
        try:
            cart = json.loads(cart_cookie) if cart_cookie else []
        except json.JSONDecodeError:
            cart = []

        product_in_cart = next((item for item in cart if item['slug'] == slug), None)

        if product_in_cart:
            product_in_cart['quantity'] += 1
        else:
            cart.append({'slug': slug, 'quantity': 1})

        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(
            'cart',
            json.dumps(cart),
            max_age=60 * 60 * 24 * 7,
            httponly=True,
            samesite='Lax',
        )
        return response

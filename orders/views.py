import json
import urllib.parse

from django.core.checks import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from products.models import Product
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .cart_utils import get_cart_items_and_total



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
            if cart_cookie:
                decoded_cart = urllib.parse.unquote(cart_cookie)
                raw_cart = json.loads(decoded_cart)
            else:
                raw_cart = []
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

        encoded_cart = urllib.parse.quote(json.dumps(cart))

        response.set_cookie(
            'cart',
            encoded_cart,
            max_age=60 * 60 * 24 * 7,
            samesite='Lax',
        )
        return response


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        account = getattr(user, 'account', None)

        is_registration_complete = True
        missing_fields = []

        if not account:
            is_registration_complete = False

        else:
            for field in ['first_name', 'last_name', 'phone_number']:
                if not getattr(account, field, None):
                    missing_fields.append(field.replace('_', ' '))
            address = getattr(account, 'default_shipping', None)
            if not address:
                missing_fields.append("shipping address")
            else:
                for field in ['street_address', 'city', 'postal_code', 'country']:
                    if not getattr(address, field, None):
                        missing_fields.append(field.replace('_', ' '))

            if missing_fields:
                is_registration_complete = False

        cart_items, cart_total = get_cart_items_and_total(request)

        if not cart_items:
            return redirect('cart')

        context = {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'account': account,
            'shipping_address': getattr(account, 'default_shipping', None),
            'isRegistrationComplete': is_registration_complete,
        }

        return render(request, 'orders/checkout.html', context)
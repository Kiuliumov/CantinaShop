import json
import urllib.parse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from products.models import Product
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .cart_utils import get_cart_items_and_total
from .models import Order


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

        return render(request, 'shopping_cart/checkout.html', context)


class OrderCreateView(LoginRequiredMixin, View):
    COOLDOWN_SECONDS = 60

    def post(self, request, *args, **kwargs):
        last_order_time = request.session.get('last_order_time')
        now = timezone.now()

        if last_order_time:
            try:
                last_time = timezone.datetime.fromisoformat(last_order_time)
                if timezone.is_naive(last_time):
                    last_time = timezone.make_aware(last_time, timezone.get_current_timezone())
            except ValueError:
                last_time = None

            if last_time:
                elapsed = (now - last_time).total_seconds()
                if elapsed < self.COOLDOWN_SECONDS:
                    raise PermissionDenied("Please wait before placing another order.")

        try:
            account = request.user.account
        except AttributeError:
            raise PermissionDenied("User account not found.")

        cart_cookie = request.COOKIES.get('cart')
        if not cart_cookie:
            raise PermissionDenied("Cart is empty.")

        try:
            decoded_cart = urllib.parse.unquote(cart_cookie)
            raw_cart = json.loads(decoded_cart)
        except json.JSONDecodeError:
            raise PermissionDenied("Invalid cart data.")

        if not raw_cart:
            raise PermissionDenied("Cart is empty.")

        payment_option = request.POST.get('payment_method')
        if not payment_option:
            raise PermissionDenied("Payment method required.")

        total_price = 0
        product_quantities = []

        for item in raw_cart:
            slug = item.get('slug')
            quantity = item.get('quantity', 1)
            if not slug or quantity < 1:
                continue
            try:
                product = Product.objects.get(slug=slug)
                total_price += product.price * quantity
                product_quantities.append({
                    'product_id': product.id,
                    'quantity': quantity
                })
            except Product.DoesNotExist:
                continue

        if not product_quantities:
            raise PermissionDenied("No valid products in cart.")

        order = Order.objects.create(
            account=account,
            payment_option=payment_option,
            total_price=total_price,
            product_quantities=product_quantities,
            status='pending'
        )

        request.session['last_order_time'] = now.isoformat()

        response = render(request, 'orders/order-confirmation.html', {'order': order})
        response.delete_cookie('cart')

        return response
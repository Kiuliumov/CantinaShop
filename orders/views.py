import json
import urllib.parse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from common.tasks import send_order_confirmation_email_task
from products.models import Product
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .cart_utils import get_cart_items_and_total
from .models import Order


class AddToCartView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        if not product.is_available:
            messages.error(request, "Product is not available for purchase.")
            return HttpResponseBadRequest("Product is not available for purchase.")

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

        messages.success(request, f"Added {quantity} x '{product.name}' to your cart.")
        products_list_url = reverse('product-list')
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', products_list_url))

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

        cart_items, cart_total = get_cart_items_and_total(request)

        if not cart_items:
            messages.error(request, "Your cart is empty. Please add items before checking out.")
            return redirect('cart')

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
                messages.warning(request, f"Please complete your profile: missing {', '.join(missing_fields)}.")
                return redirect('account')


        context = {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'account': account,
            'shipping_address': getattr(account, 'default_shipping', None),
            'isRegistrationComplete': is_registration_complete,
        }

        return render(request, 'shopping_cart/checkout.html', context)


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            account = request.user.account
        except AttributeError:
            messages.error(request, "User account not found.")
            raise PermissionDenied()

        cart_cookie = request.COOKIES.get('cart')
        if not cart_cookie:
            messages.error(request, "Your cart is empty.")
            raise PermissionDenied()

        try:
            decoded_cart = urllib.parse.unquote(cart_cookie)
            raw_cart = json.loads(decoded_cart)
        except json.JSONDecodeError:
            messages.error(request, "Invalid cart data.")
            raise PermissionDenied()

        if not raw_cart:
            messages.error(request, "Your cart is empty.")
            raise PermissionDenied()

        payment_option = request.POST.get('payment_method')
        if not payment_option:
            messages.error(request, "Please select a payment method.")
            raise PermissionDenied()

        total_price = 0
        product_data = []

        for item in raw_cart:
            slug = item.get('slug')
            quantity = item.get('quantity', 1)
            if not slug or quantity < 1:
                continue
            try:
                product = Product.objects.get(slug=slug)
                total_price += product.price * quantity
                product_data.append({
                    'product_id': product.id,
                    'name': product.name,
                    'slug': product.slug,
                    'price': str(product.price),
                    'quantity': quantity,
                    'image_url': product.image_url
                })
            except Product.DoesNotExist:
                continue

        if not product_data:
            messages.error(request, "No valid products in your cart.")
            raise PermissionDenied()

        order = Order.objects.create(
            account=account,
            payment_option=payment_option,
            total_price=total_price,
            order_data=product_data,
            status='pending'
        )

        send_order_confirmation_email_task.delay(request.user.id, order.id)

        messages.success(request, "Your order has been placed successfully!")

        response = render(request, 'orders/order-confirmation.html', {'order': order})
        response.delete_cookie('cart')

        return response

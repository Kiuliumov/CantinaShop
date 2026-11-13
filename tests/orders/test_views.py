import json
from urllib.parse import unquote

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from orders.models import Order


class TestAddToCart:
    @pytest.mark.parametrize("quantity, expected", [("3", 3), ("bad", 1), ("0", 1)])
    def test__add_product__sets_quantity_cookie(self, client, product, quantity, expected):
        response = client.get(reverse("cart_save", args=[product.slug]), {"quantity": quantity})
        assert json.loads(unquote(response.cookies["cart"].value)) == [{"slug": product.slug, "quantity": expected}]

    def test__add_unavailable_product__rejects(self, client, product):
        product.is_available = False
        product.save()
        assert client.get(reverse("cart_save", args=[product.slug])).status_code == 400


class TestCheckout:
    def test__checkout_empty_cart__redirects_to_cart(self, auth_client):
        assertRedirects(auth_client.get(reverse("checkout")), reverse("cart"))

    def test__checkout_incomplete_profile__redirects_to_account(self, cart_client):
        assertRedirects(cart_client.get(reverse("checkout")), reverse("account"))

    def test__checkout_complete_profile__renders_summary(self, cart_client, shipping_account):
        response = cart_client.get(reverse("checkout"))
        assertTemplateUsed(response, "shopping_cart/checkout.html")
        assert response.context["isRegistrationComplete"]


class TestOrderCreation:
    def test__place_order__persists_total_clears_cart_and_queues_email(
        self, cart_client, shipping_account, product, queued_emails
    ):
        response = cart_client.post(reverse("order"), {"payment_method": "credit_card"})
        order = Order.objects.get()
        assertTemplateUsed(response, "orders/order-confirmation.html")
        assert order.total_price == product.price * 2
        assert order.order_data[0]["quantity"] == 2
        assert response.cookies["cart"]["max-age"] == 0
        queued_emails["send_order_confirmation_email_task"].assert_called_once_with(shipping_account.user_id, order.pk)

    def test__place_order_without_payment__forbidden(self, cart_client):
        assert cart_client.post(reverse("order")).status_code == 403
        assert not Order.objects.exists()

    @pytest.mark.parametrize("cookie", ["", "invalid", "%5B%5D"])
    def test__place_order_without_valid_cart__forbidden(self, auth_client, cookie):
        auth_client.cookies["cart"] = cookie
        assert auth_client.post(reverse("order"), {"payment_method": "credit_card"}).status_code == 403
        assert not Order.objects.exists()

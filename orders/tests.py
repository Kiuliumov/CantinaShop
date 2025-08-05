from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import Account
from products.models import Product, Category
from orders.models import Order
from decimal import Decimal
from django.urls import reverse
import json
import urllib.parse

User = get_user_model()

class OrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='example@example.com', password='pass12345')
        self.user.is_active = True
        self.user.save()

        self.category = Category.objects.create(name="Sunglasses")
        self.product = Product.objects.create(
            name="Test Sunglasses",
            slug="test-sunglasses",
            description="Test description",
            price=Decimal('99.99'),
            category=self.category,
            is_available=True,
            image_url="https://example.com/image.jpg"
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_order_model_str(self):
        order = Order.objects.create(
            account=self.user.account,
            payment_option="credit_card",
            order_data={"items": []},
            total_price=Decimal("199.99"),
            status="pending"
        )
        self.assertEqual(str(order), f"Order #{order.id} by {self.user.username}")

    def test_get_cart_items_and_total(self):
        from orders.cart_utils import get_cart_items_and_total

        cart = [{'slug': 'test-sunglasses', 'quantity': 2}]
        encoded_cart = urllib.parse.quote(json.dumps(cart))
        self.client.cookies['cart'] = encoded_cart
        response = self.client.get('/')
        request = response.wsgi_request
        request.COOKIES = {'cart': encoded_cart}

        items, total = get_cart_items_and_total(request)
        self.assertEqual(len(items), 1)
        self.assertEqual(total, self.product.price * 2)

    def test_checkout_redirects_with_empty_cart(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('cart'), response.url)

    def test_create_order(self):
        cart_data = [{'slug': self.product.slug, 'quantity': 1}]
        encoded_cart = urllib.parse.quote(json.dumps(cart_data))
        self.client.cookies['cart'] = encoded_cart

        response = self.client.post(reverse('order'), {
            'payment_method': 'credit_card'
        })

        if response.status_code == 302:
            response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order-confirmation.html')
        self.assertTrue(Order.objects.exists())

        order = Order.objects.first()
        self.assertEqual(order.total_price, self.product.price)
        self.assertEqual(order.status, 'pending')

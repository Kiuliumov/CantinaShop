from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import ChatMessage
from products.models import Product, Category
from django.utils import timezone

User = get_user_model()

class APITestSuite(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
            is_staff=True,
            is_active=True
        )
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
            is_active=True
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="StrongPass123!",
            is_active=True
        )
        self.category = Category.objects.create(name="Category 1")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.0,
            is_available=True,
            category=self.category
        )
        self.client = APIClient()

    def test_chat_messages_auth_required(self):
        url = reverse('chat-messages-api-base', args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_own_messages(self):
        self.client.login(username="user1", password="StrongPass123!")
        ChatMessage.objects.create(sender=self.user1, recipient=self.admin, message="Hi", timestamp=timezone.now())
        url = reverse('chat-messages-api-base', args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)

    def test_user_cannot_view_others_messages(self):
        self.client.login(username="user1", password="StrongPass123!")
        url = reverse('chat-messages-api-base', args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_any_messages(self):
        self.client.login(username="admin", password="StrongPass123!")
        url = reverse('chat-messages-api-base', args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_default(self):
        url = reverse('product-list-api-base')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)

    def test_filter_by_id(self):
        url = reverse('product-list-api-base') + f'?id={self.product.id}'
        response = self.client.get(url)
        self.assertEqual(len(response.data['products']), 1)

    def test_search_filter(self):
        url = reverse('product-list-api-base') + '?search=Test'
        response = self.client.get(url)
        self.assertGreaterEqual(len(response.data['products']), 1)

    def test_category_filter(self):
        url = reverse('product-list-api-base') + f'?category={self.category.id}'
        response = self.client.get(url)
        self.assertGreaterEqual(len(response.data['products']), 1)

    def test_availability_filter(self):
        url = reverse('product-list-api-base') + '?availability=available'
        response = self.client.get(url)
        self.assertGreaterEqual(len(response.data['products']), 1)

    def test_price_range_filter(self):
        url = reverse('product-list-api-base') + '?min_price=5&max_price=15'
        response = self.client.get(url)
        self.assertGreaterEqual(len(response.data['products']), 1)

    def test_sorting(self):
        url = reverse('product-list-api-base') + '?sort=price_desc'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_unauthorized(self):
        url = reverse('product-list-api-base')
        response = self.client.post(url, {"name": "New Product", "price": 100.0})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_forbidden_for_non_admin(self):
        self.client.login(username="user1", password="StrongPass123!")
        url = reverse('product-list-api-base')
        response = self.client.post(url, {
            "name": "Unauthorized Product",
            "price": 50.0,
            "description": "Should not be created",
            "is_available": True,
            "category": self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_create_product_authorized(self):
        self.client.login(username="admin", password="StrongPass123!")
        url = reverse('product-list-api-base')
        response = self.client.post(url, {
            "name": "New Product",
            "price": 100.0,
            "description": "Test desc",
            "is_available": True,
            "category": self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

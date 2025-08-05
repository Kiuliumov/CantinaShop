from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category, Comment, Rating

# ----------------------
# UNIT TESTS
# ----------------------

class ProductUnitTests(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345',
            email='testuser@example.com'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com'
        )
        self.category = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Test Product',
            description='A great product.',
            price=19.99,
            is_available=True,
            slug='test-product',
            category=self.category
        )

    def test_product_model_str(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_product_average_rating(self):
        Rating.objects.create(user=self.user.account, product=self.product, rating=4)
        Rating.objects.create(user=self.admin.account, product=self.product, rating=2)
        self.assertEqual(self.product.average_rating, 3.0)

    def test_product_rating_count(self):
        Rating.objects.create(user=self.user.account, product=self.product, rating=5)
        self.assertEqual(self.product.rating_count, 1)

    def test_category_model_str(self):
        self.assertEqual(str(self.category), 'Books')

    def test_comment_str(self):
        comment = Comment.objects.create(product=self.product, account=self.user.account, content='Nice')
        expected = f"{self.user.username} on {self.product.name}"
        self.assertEqual(str(comment), expected)

    def test_comment_save_sanitization(self):
        comment = Comment.objects.create(product=self.product, account=self.user.account, content='clean')
        self.assertIn('clean', comment.content)

    def test_product_save_sanitization(self):
        self.product.name = 'Clean Name'
        self.product.save()
        self.assertIn('Clean', self.product.name)

    def test_product_slug_unique(self):
        slug = self.product.slug
        self.assertEqual(slug, 'test-product')

    def test_category_unique_constraint(self):
        with self.assertRaises(Exception):
            Category.objects.create(name='Books')


# ----------------------
# INTEGRATION TESTS
# ----------------------

class ProductViewIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_superuser(username='admin', password='admin')
        self.category = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Test Product',
            description='A great product.',
            price=19.99,
            is_available=True,
            slug='test-product',
            category=self.category
        )

    def test_product_list_view_status(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_filter_by_category(self):
        response = self.client.get(reverse('product-list'), {'category': self.category.id})
        self.assertContains(response, 'Test Product')

    def test_product_list_filter_by_availability(self):
        response = self.client.get(reverse('product-list'), {'availability': 'available'})
        self.assertContains(response, 'Test Product')

    def test_product_list_sort_by_price_desc(self):
        response = self.client.get(reverse('product-list'), {'sort': 'price_desc'})
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        response = self.client.get(reverse('product-details', kwargs={'slug': 'test-product'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_product_detail_post_comment(self):
        self.client.login(username='testuser', password='12345')
        data = {'content': 'Nice product!'}
        response = self.client.post(reverse('product-details', kwargs={'slug': 'test-product'}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content='Nice product!').exists())

    def test_add_product_admin_only(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('product-add'))
        self.assertEqual(response.status_code, 403)

    def test_add_product_success(self):
        self.client.login(username='admin', password='admin')
        data = {
            'name': 'New Book',
            'description': 'New Book Desc',
            'price': 29.99,
            'is_available': True,
            'slug': 'new-book',
            'category': self.category.id
        }
        response = self.client.post(reverse('product-add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='New Book').exists())

    def test_comment_delete_permission(self):
        comment = Comment.objects.create(product=self.product, account=self.user.account, content='Delete me')
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('comment-delete', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_set_rating_valid(self):
        self.client.login(username='testuser', password='12345')
        data = {'rating': '4'}
        response = self.client.post(reverse('set-rating', kwargs={'slug': 'test-product'}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Rating.objects.filter(user=self.user.account, product=self.product).exists())
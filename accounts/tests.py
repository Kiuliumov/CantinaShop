from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', is_active=True)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/authentication/register.html')

    def test_register_view_post_valid(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('email_confirmation_sent'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertFalse(new_user.is_active)

    def test_activate_account_valid(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse('activation_success'))

    def test_activate_account_invalid(self):
        response = self.client.get(reverse('activate', kwargs={'uidb64': 'invalid', 'token': 'invalidtoken'}))
        self.assertRedirects(response, reverse('activation_invalid'))

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/authentication/login.html')

    def test_login_view_post_valid(self):
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, reverse('index'))

    def test_login_view_post_invalid(self):
        data = {'username': 'wronguser', 'password': 'wrongpass'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password")
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))
    def test_account_update_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/account_info.html')

    def test_account_update_view_post(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'country_code': 'US',
            'street_address': '123 Main St',
            'city': 'Townsville',
            'state': 'State',
            'postal_code': '12345',
            'country': 'USA',
        }
        response = self.client.post(reverse('account'), data)
        self.assertRedirects(response, reverse('account'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.account.first_name, 'Test')
        self.assertEqual(self.user.account.default_shipping.street_address, '123 Main St')

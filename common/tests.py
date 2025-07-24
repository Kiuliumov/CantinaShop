from django.test import TestCase

# Create your tests here.


from django.test import TestCase
from django.urls import reverse
from common.forms import ContactMessageForm
from common.models import ContactMessage
from common.views import Index, About, ContactView

# Unit Tests
class StaticViewTests(TestCase):

    def test_index_template_used(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/index.html')

    def test_about_template_used(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/about.html')


class ContactViewTests(TestCase):

    def test_contact_template_used(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/contacts.html')

    def test_contact_form_in_context(self):
        response = self.client.get(reverse('contact'))
        self.assertIsInstance(response.context['form'], ContactMessageForm)


# Integration Tests
class ContactFormIntegrationTests(TestCase):

    def test_valid_contact_form_submission(self):
        data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'Hello, this is a test message.'
        }

        response = self.client.post(reverse('contact'), data)

        self.assertRedirects(response, reverse('index'))

        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Jane Doe')
        self.assertEqual(msg.email, 'jane@example.com')
        self.assertEqual(msg.message, 'Hello, this is a test message.')

    def test_invalid_contact_form_submission(self):
        data = {
            'name': '',
            'email': 'not-an-email',
            'message': ''
        }

        response = self.client.post(reverse('contact'), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/contacts.html')

        form = response.context['form']
        self.assertFormError(form, 'name', 'This field is required.')
        self.assertFormError(form, 'message', 'This field is required.')
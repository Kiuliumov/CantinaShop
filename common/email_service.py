import asyncio

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse

EMAIL_SENDER = 'no-reply@cantinashop.com'

class EmailService:

    @staticmethod
    def send_confirmation_email(request, user):
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )

        subject = 'Activate your CantinaShop account'
        context = {
            'user': user,
            'domain': current_site.domain,
            'activation_link': activation_link,
        }

        html_content = render_to_string('accounts/authentication/email_for_confirmation.html', context)

        email = EmailMultiAlternatives(subject, '', EMAIL_SENDER, [user.email])
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

    @staticmethod
    async def send_order_confirmation_email_async(request, user, order):
        """
        Asynchronously send order confirmation email to user.
        """
        subject = f"Your Order #{order.id} Confirmation"
        context = {
            'user': user,
            'order': order,
            'request': request,
        }

        html_content = render_to_string('orders/order_confirmation_email.html', context)
        text_content = 'Thank you for your order!'

        email = EmailMultiAlternatives(subject, text_content, EMAIL_SENDER, [user.email])
        email.attach_alternative(html_content, "text/html")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, email.send, False)

    @staticmethod
    def send_order_confirmation_email(request, user, order):
        """
        Synchronous wrapper to call the async method.
        """
        asyncio.run(EmailService.send_order_confirmation_email_async(request, user, order))
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from common.tasks import send_confirmation_email_task, send_order_confirmation_email_task
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

        send_confirmation_email_task.delay(user.pk, current_site.domain, activation_link, subject)

    @staticmethod
    def send_order_confirmation_email(request, user, order):
        send_order_confirmation_email_task.delay(user.pk, order.id)
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
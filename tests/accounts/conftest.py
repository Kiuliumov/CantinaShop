import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@pytest.fixture
def registration_data():
    return dict(username="newbuyer", email="new@example.com", password1="SecurePass123!", password2="SecurePass123!")


@pytest.fixture
def activation_args(user):
    user.is_active = False
    user.save()
    return [urlsafe_base64_encode(force_bytes(user.pk)), default_token_generator.make_token(user)]

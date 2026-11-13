import pytest
from django.contrib.auth import authenticate


class TestEmailOrUsernameBackend:
    @pytest.mark.parametrize("field", ["username", "email"])
    def test__authenticate_valid_credentials__returns_user(self, user, field):
        assert authenticate(username=getattr(user, field), password="SecurePass123!") == user

    def test__authenticate_wrong_password__returns_none(self, user):
        assert authenticate(username=user.username, password="wrong") is None

    def test__authenticate_inactive_user__returns_none(self, user):
        user.is_active = False
        user.save()
        assert authenticate(username=user.email, password="SecurePass123!") is None

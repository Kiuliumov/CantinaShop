import pytest


class TestUserManager:
    def test__create_user__normalizes_email_and_hashes_password(self, db, django_user_model):
        user = django_user_model.objects.create_user(
            email="Jane@EXAMPLE.COM", username="Jane", password="SecurePass123!"
        )
        assert user.email == "Jane@example.com"
        assert user.check_password("SecurePass123!")

    @pytest.mark.parametrize("field", ["email", "username"])
    def test__create_user_missing_identity__raises_value_error(self, db, django_user_model, field):
        data = dict(email="jane@example.com", username="Jane")
        data[field] = ""
        with pytest.raises(ValueError, match="must be provided"):
            django_user_model.objects.create_user(**data)

    def test__create_superuser__grants_staff_and_superuser(self, db, django_user_model):
        user = django_user_model.objects.create_superuser("admin@example.com", "admin", "password")
        assert user.is_staff and user.is_superuser

    @pytest.mark.parametrize("field", ["is_staff", "is_superuser"])
    def test__create_superuser_invalid_flags__raises_value_error(self, db, django_user_model, field):
        with pytest.raises(ValueError, match=field):
            django_user_model.objects.create_superuser("admin@example.com", "admin", **{field: False})


class TestAccount:
    def test__str__includes_username(self, user):
        assert str(user.account) == f"{user.username}'s Account"

    def test__delete_user__cascades_to_account(self, user):
        account = user.account
        user.delete()
        assert not type(account).objects.filter(pk=account.pk).exists()

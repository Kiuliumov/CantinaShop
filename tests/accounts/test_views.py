import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed


@pytest.mark.django_db
class TestAuthenticationViews:
    @pytest.mark.parametrize("route", ["register", "login"])
    def test__get_auth_page__renders_template(self, client, route):
        response = client.get(reverse(route))
        assert response.status_code == 200
        assertTemplateUsed(response, f"accounts/authentication/{route}.html")

    def test__register__creates_inactive_user_and_queues_email(
        self, client, registration_data, queued_emails, django_user_model
    ):
        response = client.post(reverse("register"), registration_data)
        assertRedirects(response, reverse("email_confirmation_sent"))
        assert not django_user_model.objects.get(username="newbuyer").is_active
        queued_emails["send_confirmation_email_task"].assert_called_once()

    def test__activate_valid_token__activates_and_logs_in(self, client, user, activation_args):
        response = client.get(reverse("activate", args=activation_args))
        user.refresh_from_db()
        assert user.is_active
        assert client.session["_auth_user_id"] == str(user.pk)
        assertRedirects(response, reverse("activation_success"))

    def test__activate_invalid_token__redirects_to_error(self, client):
        assertRedirects(client.get(reverse("activate", args=["invalid", "invalid"])), reverse("activation_invalid"))

    def test__login_valid_credentials__starts_session(self, client, user):
        response = client.post(reverse("login"), dict(username=user.username, password="SecurePass123!"))
        assertRedirects(response, reverse("index"))
        assert client.session["_auth_user_id"] == str(user.pk)

    def test__login_invalid_credentials__shows_form_error(self, client):
        response = client.post(reverse("login"), dict(username="unknown", password="wrong"))
        assert "Invalid username/email or password" in response.context["form"].non_field_errors()

    def test__logout__ends_session(self, auth_client):
        assertRedirects(auth_client.post(reverse("logout")), reverse("index"))
        assert "_auth_user_id" not in auth_client.session

    def test__deactivate__disables_user_and_ends_session(self, auth_client, user):
        assertRedirects(auth_client.post(reverse("account_deactivate")), reverse("index"))
        user.refresh_from_db()
        assert not user.is_active
        assert "_auth_user_id" not in auth_client.session

    def test__password_reset__queues_email(self, client, user, queued_emails):
        assertRedirects(client.post(reverse("password_reset"), {"email": user.email}), reverse("password_reset_done"))
        queued_emails["send_password_reset_email_task"].assert_called_once()


class TestAccountView:
    def test__get_account__renders_profile(self, auth_client):
        assertTemplateUsed(auth_client.get(reverse("account")), "accounts/account_info.html")

    def test__post_account__saves_profile_and_shipping(self, auth_client, user):
        response = auth_client.post(
            reverse("account"), dict(username=user.username, first_name="Jane", street_address="123 Main St")
        )
        assertRedirects(response, reverse("account"))
        user.account.refresh_from_db()
        assert user.account.first_name == "Jane"
        assert user.account.default_shipping.street_address == "123 Main St"

from accounts.forms import AccountForm, RegistrationForm


class TestRegistrationForm:
    def test__validate_new_user__accepts(self, db, registration_data):
        assert RegistrationForm(registration_data).is_valid()

    def test__validate_duplicate_email__rejects(self, user, registration_data):
        registration_data["email"] = user.email
        form = RegistrationForm(registration_data)
        assert not form.is_valid()
        assert "email" in form.errors


class TestAccountForm:
    def test__save_address__updates_existing_shipping(self, shipping_account):
        form = AccountForm(dict(username="renamed", street_address="456 Main St"), instance=shipping_account)
        assert form.is_valid(), form.errors
        account = form.save()
        assert account.user.username == "renamed"
        assert account.default_shipping.street_address == "456 Main St"
        assert account.addresses.count() == 1

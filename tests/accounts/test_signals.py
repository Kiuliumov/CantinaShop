from accounts.models import Account


class TestUserSignals:
    def test__create_user__creates_account(self, user):
        assert Account.objects.filter(user=user).count() == 1

    def test__save_user__does_not_duplicate_account(self, user):
        user.save()
        assert Account.objects.filter(user=user).count() == 1

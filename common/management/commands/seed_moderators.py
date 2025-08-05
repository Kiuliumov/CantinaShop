from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

User = get_user_model()

class Command(BaseCommand):
    help = "Ensure all users in the 'Moderator' group are marked as staff (is_staff=True)."

    def handle(self, *args, **kwargs):
        try:
            group = Group.objects.get(Q(name="Moderator") | Q(name="Administrator"))
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("The 'Moderators' group does not exist."))
            return

        users = group.user_set.all()
        updated = 0

        for user in users:
            if not user.is_staff:
                user.is_staff = True
                user.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Marked {updated} user(s) in 'Moderators' group as staff."
        ))

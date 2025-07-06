from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account, UserModel

@receiver(post_save, sender=UserModel)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

@receiver(post_save, sender=UserModel)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()

import secrets
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import models

from accounts.models import UserModel


# Create your models here.

class APIKey(models.Model):
    key = models.CharField(max_length=40, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at and timezone.now() >= self.expires_at

    def __str__(self):
        return f"APIKey(user={self.user}, key={self.key[:6]}...)"
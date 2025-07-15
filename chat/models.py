from django.db import models

from accounts.models import Account, UserModel

from django.db import models
from accounts.models import Account

class ChatMessage(models.Model):
    sender = models.ForeignKey(UserModel, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserModel, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username} at {self.timestamp}: {self.message}"

    @property
    def avatar_url(self):
        if self.sender.is_staff or self.sender.is_superuser:
            return "/static/images/admin.jpg"
        return self.sender.account.profile_picture_url or "/static/images/avatar.png"

    @property
    def is_from_admin(self):
        return self.sender.is_staff or self.sender.is_superuser

    class Meta:
        ordering = ['timestamp']
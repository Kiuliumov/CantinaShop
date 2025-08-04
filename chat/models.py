from django.db import models
from django.templatetags.static import static

from accounts.models import UserModel


class ChatMessage(models.Model):
    sender = models.ForeignKey(UserModel, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserModel, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_from_admin = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username} at {self.timestamp}: {self.message}"

    @property
    def avatar_url(self):
        if self.is_from_admin:
            return static('images/admin.jpg')
        return self.sender.account.profile_picture_url or static('images/avatar.png')

    class Meta:
        ordering = ['timestamp']

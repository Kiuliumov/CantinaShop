from django.db import models

from accounts.models import Account


class ChatMessage(models.Model):
    user = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} at {self.timestamp}: {self.message}"

    @property
    def avatar_url(self):
        if self.user and self.user.profile_picture_url:
            return self.user.profile_picture_url
        return None
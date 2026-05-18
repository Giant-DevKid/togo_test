from django.db import models

from account.models import User


class ConversationSession(models.Model):

    phone_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=100, default="START")
    current_menu = models.CharField(max_length=100, null=True, blank=True)
    current_action = models.CharField(max_length=100, null=True, blank=True)
    context = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    last_interaction = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reset_context(self):
        self.context = {}
        self.save()

from django.db import models
from account.models import User


class ConversationSession(models.Model):

    STATES = [
        ("START", "START"),
        ("ASK_ROLE", "ASK_ROLE"),
        ("ASK_EMAIL", "ASK_EMAIL"),
        ("VERIFY_OTP", "VERIFY_OTP"),
        ("ASK_FIRST_NAME", "ASK_FIRST_NAME"),
        ("COMPLETED", "COMPLETED"),
    ]

    phone_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="whatsapp_sessions",
    )
    state = models.CharField(max_length=50, choices=STATES, default="START")

    context = models.JSONField(default=dict)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

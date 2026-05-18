
from django.db import models
from account.models import User


class Event(models.Model):

    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    event_name = models.CharField(max_length=255)

    location = models.TextField()

    start_date = models.DateField()

    end_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name
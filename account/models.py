import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
    Group
)


def upload_data(instance, filename):
    return f"users/{instance.id}/{filename}"

class UserManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user
    
    def create_user(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            email,
            password,
            **extra_fields
        )


    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        user = self._create_user(
            email,
            password,
            **extra_fields
        )

        developer_group, _ = Group.objects.get_or_create(
            name="developer"
        )

        user.groups.add(developer_group)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    PASSENGER = "passenger"
    RIDER = "rider"
    EVENT_ORGANISER = "event_organiser"
    TOUR_GUIDE = "tour_guide"


    USER_TYPES = [
        (PASSENGER, "Passenger"),
        (RIDER, "Rider"),
        (EVENT_ORGANISER, "Event Organiser"),
        (TOUR_GUIDE, "Tour Guide"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    first_name = models.CharField(max_length=125, null=True, blank=True)
    last_name = models.CharField(max_length=125, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    user_picture = models.ImageField(upload_to=upload_data, null=True, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    otp_request_time = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(choices=USER_TYPES, max_length=20, default=PASSENGER)
    online_status = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
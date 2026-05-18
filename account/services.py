import random
import traceback

from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

OTP_EXPIRATION_MINUTES = 10


def generate_otp():
    return str(random.randint(100000, 999999))


def otp_is_expired(user):

    if not user.otp_request_time:
        return True

    expiration_time = (
        user.otp_request_time +
        timedelta(minutes=OTP_EXPIRATION_MINUTES)
    )

    return timezone.now() > expiration_time


def get_existing_user(phone_number):

    return User.objects.filter(
        phone_no=phone_number,
        is_verified=True
    ).first()

def create_user_account(email, user_type, phone_no=None):

    existing_user = User.objects.filter(
        email=email,
        is_verified=True
    ).first()

    if existing_user:
        raise ValidationError(
            "An account with this email already exists."
        )

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "user_type": user_type,
            "phone_no": phone_no,
        }
    )

    return user

def send_verification_otp(user):

    try:

        otp = generate_otp()

        user.otp = otp

        user.otp_request_time = timezone.now()

        user.save()

        send_mail(
            "Verify Your Account",
            f"Your OTP is {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        print("OTP EMAIL SENT")

    except Exception as e:

        print("EMAIL ERROR:", str(e))

        traceback.print_exc()

        raise e
    

def verify_user_otp(user, otp):

    if otp_is_expired(user):
        return False, "OTP expired"

    if user.otp != otp:
        return False, "Invalid OTP"

    user.is_verified = True
    user.otp = None
    user.save()

    return True, "OTP verified"

def generate_tokens(user):

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
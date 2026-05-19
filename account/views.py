from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
)

from .services import (
    create_user_account,
    send_verification_otp,
    verify_user_otp,
    generate_tokens,
)
from .models import User


@api_view(["POST"])
def register_user(request):

    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = create_user_account(
        email=serializer.validated_data["email"],
        user_type=serializer.validated_data["user_type"],
        phone_no=serializer.validated_data.get("phone_no"),
    )

    send_verification_otp(user)

    return Response({"message": "OTP sent successfully"})


@api_view(["POST"])
def verify_otp(request):

    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.get(email=serializer.validated_data["email"])

    success, message = verify_user_otp(user, serializer.validated_data["otp"])

    if not success:
        return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

    tokens = generate_tokens(user)
    return Response({"message": "Verification successful", "tokens": tokens})

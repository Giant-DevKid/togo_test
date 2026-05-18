from rest_framework import serializers

from .models import User

class RegisterSerializer(serializers.Serializer):

    email = serializers.EmailField()
    user_type = serializers.CharField()
    phone_no = serializers.CharField(required=False)


class VerifyOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()
    otp = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_no",
            "user_type",
            "is_verified",
        ]
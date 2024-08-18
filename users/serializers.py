from rest_framework import serializers
from .models import CustomUser
from .utils import standardize_phone_number, is_valid_phone_number


class UserRegistrationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=13)
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, default=1)

    def validate_phone(self, value):
        try:
            phone = standardize_phone_number(value)
        except ValueError:
            raise serializers.ValidationError("Invalid phone number format")

        if not is_valid_phone_number(phone):
            raise serializers.ValidationError("Invalid phone number")

        return phone

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value


class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField()
    verification_code = serializers.CharField(max_length=6)

    def validate_phone(self, value):
        try:
            return standardize_phone_number(value)
        except ValueError:
            raise serializers.ValidationError("Invalid phone number format")


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        try:
            return standardize_phone_number(value)
        except ValueError:
            raise serializers.ValidationError("Invalid phone number format")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'phone', 'user_type', 'is_phone_verified')
        read_only_fields = ('is_phone_verified',)


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        try:
            return standardize_phone_number(value)
        except ValueError:
            raise serializers.ValidationError("Invalid phone number format")

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
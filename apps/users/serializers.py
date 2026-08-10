from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    telegram_url = serializers.SerializerMethodField()
    is_author = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "telegram_username",
            "telegram_url",
            "avatar",
            "bio",
            "role",
            "is_author",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "is_author", "telegram_url", "date_joined"]

    def get_telegram_url(self, obj) -> str | None:
        if not obj.telegram_username:
            return None
        username = obj.telegram_username.lstrip("@")
        return f"https://t.me/{username}"

    def validate_telegram_username(self, value):
        return value.strip().lstrip("@")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
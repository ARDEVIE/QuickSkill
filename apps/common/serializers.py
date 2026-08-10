from rest_framework import serializers


class AuthorSerializer(serializers.Serializer):
    """Minimal read-only representation of a user, safe to nest in other serializers."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    telegram_url = serializers.SerializerMethodField()

    def get_telegram_url(self, obj) -> str | None:
        username = getattr(obj, "telegram_username", "")
        if not username:
            return None
        return f"https://t.me/{username.lstrip('@')}"

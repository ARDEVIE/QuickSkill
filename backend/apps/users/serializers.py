# Django modules
from django.contrib.auth.password_validation import validate_password

# Third-party modules
from rest_framework import serializers

# Project modules
from apps.users.models import CustomUser


class UserContributionStatsMixin:
    '''Contribution/activity counters shared by the own-profile and public-profile serializers.'''

    def get_courses_count(self, obj) -> int:
        return obj.authored_courses.filter(is_published=True).count()

    def get_materials_count(self, obj) -> int:
        return obj.resources.count()

    def get_answers_count(self, obj) -> int:
        return obj.comments.count()

    def get_helpful_votes(self, obj) -> int:
        from apps.articles.models import CommentVote
        return CommentVote.objects.filter(comment__user=obj, value=1).count()


class UserSerializer(UserContributionStatsMixin, serializers.ModelSerializer):
    '''Own-profile representation for /api/users/me/; email/role/is_author are read-only.'''

    telegram_url = serializers.SerializerMethodField()
    is_author = serializers.BooleanField(read_only=True)
    courses_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    helpful_votes = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'telegram_username',
            'telegram_url',
            'avatar',
            'bio',
            'study_program',
            'study_year',
            'role',
            'is_author',
            'courses_count',
            'materials_count',
            'answers_count',
            'helpful_votes',
            'date_joined',
        ]
        read_only_fields = [
            'id', 'email', 'role', 'is_author', 'telegram_url', 'date_joined',
            'courses_count', 'materials_count', 'answers_count', 'helpful_votes',
        ]

    def get_telegram_url(self, obj) -> str | None:
        if not obj.telegram_username:
            return None
        username = obj.telegram_username.lstrip('@')
        return f'https://t.me/{username}'

    def validate_telegram_username(self, value):
        return value.strip().lstrip('@')


class PublicUserSerializer(UserContributionStatsMixin, serializers.ModelSerializer):
    '''Public-profile representation for /api/users/<username>/ — deliberately excludes email.'''

    telegram_url = serializers.SerializerMethodField()
    is_author = serializers.BooleanField(read_only=True)
    courses_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    helpful_votes = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'telegram_username',
            'telegram_url',
            'avatar',
            'bio',
            'study_program',
            'study_year',
            'role',
            'is_author',
            'courses_count',
            'materials_count',
            'answers_count',
            'helpful_votes',
            'date_joined',
        ]
        read_only_fields = fields

    def get_telegram_url(self, obj) -> str | None:
        if not obj.telegram_username:
            return None
        username = obj.telegram_username.lstrip('@')
        return f'https://t.me/{username}'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

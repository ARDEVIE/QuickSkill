# Third-party modules
from rest_framework import serializers

# Project modules
from apps.users.models import CustomUser
from apps.articles.models import Comment, Question
from apps.courses.serializers import CategorySerializer


class QuestionAuthorSerializer(serializers.ModelSerializer):
    '''Serializer to represent the author in questions and comments.'''

    display_name = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'display_name', 'profile_url']

    def get_display_name(self, obj):
        if obj.first_name or obj.last_name:
            return f'{obj.first_name} {obj.last_name}'.strip()
        return obj.username

    def get_profile_url(self, obj):
        # We assume the frontend structure or we provide a standard path
        return f'/users/{obj.username}/'


class CommentSerializer(serializers.ModelSerializer):
    user = QuestionAuthorSerializer(read_only=True)
    reply_to_user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'question', 'user', 'content', 'media_file', 'parent', 'reply_to_user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_reply_to_user(self, obj):
        if obj.parent:
            user = obj.parent.user
            if user.first_name or user.last_name:
                return f'{user.first_name} {user.last_name}'.strip()
            return user.username
        return None

class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'media_file', 'parent']

    def validate_media_file(self, value):
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Media file size must be under 10MB.')
        return value

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Comment content cannot be empty.')
        return value


class QuestionListSerializer(serializers.ModelSerializer):
    author = QuestionAuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'slug', 'author', 'category', 'created_at']


class QuestionDetailSerializer(serializers.ModelSerializer):
    author = QuestionAuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    accepted_comment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'slug', 'content',
            'author', 'category', 'accepted_comment', 'created_at', 'updated_at'
        ]

class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'slug', 'content', 'category']
        read_only_fields = ['id', 'slug']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty.')
        return value

# Third-party modules
from rest_framework import serializers

# Project modules
from apps.users.models import CustomUser
from apps.articles.models import Comment, Question
from apps.courses.serializers import CategorySerializer


def _vote_score(votes_manager):
    return sum(v.value for v in votes_manager.all())


def _user_vote(votes_manager, request):
    if not request or not request.user.is_authenticated:
        return None
    for vote in votes_manager.all():
        if vote.user_id == request.user.id:
            return vote.value
    return None


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
    question_title = serializers.CharField(source='question.title', read_only=True)
    question_slug = serializers.CharField(source='question.slug', read_only=True)
    reply_to_user = serializers.SerializerMethodField()
    vote_score = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    is_accepted = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'question', 'question_title', 'question_slug', 'user', 'content', 'media_file',
            'parent', 'reply_to_user', 'vote_score', 'user_vote', 'is_accepted', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_is_accepted(self, obj) -> bool:
        return obj.accepted_for.exists()

    def get_reply_to_user(self, obj):
        if obj.parent:
            user = obj.parent.user
            if user.first_name or user.last_name:
                return f'{user.first_name} {user.last_name}'.strip()
            return user.username
        return None

    def get_vote_score(self, obj) -> int:
        return _vote_score(obj.votes)

    def get_user_vote(self, obj):
        return _user_vote(obj.votes, self.context.get('request'))

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


class QuestionStatsMixin:
    '''Shared computed fields for question list/detail serializers.'''

    def get_preview(self, obj) -> str:
        content = (obj.content or '').strip()
        return content[:180] + ('…' if len(content) > 180 else '')

    def get_answer_count(self, obj) -> int:
        return obj.comments.count()

    def get_is_solved(self, obj) -> bool:
        return obj.accepted_comment_id is not None

    def get_vote_score(self, obj) -> int:
        return _vote_score(obj.votes)

    def get_user_vote(self, obj):
        return _user_vote(obj.votes, self.context.get('request'))


class QuestionListSerializer(QuestionStatsMixin, serializers.ModelSerializer):
    author = QuestionAuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    preview = serializers.SerializerMethodField()
    answer_count = serializers.SerializerMethodField()
    is_solved = serializers.SerializerMethodField()
    vote_score = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'slug', 'preview', 'author', 'category', 'tags', 'media_file',
            'answer_count', 'is_solved', 'vote_score', 'user_vote', 'created_at',
        ]


class QuestionDetailSerializer(QuestionStatsMixin, serializers.ModelSerializer):
    author = QuestionAuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    accepted_comment = serializers.PrimaryKeyRelatedField(read_only=True)
    answer_count = serializers.SerializerMethodField()
    is_solved = serializers.SerializerMethodField()
    vote_score = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'slug', 'content', 'media_file', 'tags',
            'author', 'category', 'accepted_comment', 'answer_count', 'is_solved',
            'vote_score', 'user_vote', 'is_favorited', 'created_at', 'updated_at',
        ]

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'slug', 'content', 'media_file', 'category', 'tags']
        read_only_fields = ['id', 'slug']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty.')
        return value

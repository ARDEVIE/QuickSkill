# Django modules
from django.db.models import Sum
from django.db.models.functions import Coalesce

# Third-party modules
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# Project modules
from apps.articles.models import Comment, CommentVote, FavoriteArticle, Question, QuestionVote
from apps.articles.permissions import IsCommentOwnerOrAdminOrReadOnly, IsQuestionAuthorOrAdminOrReadOnly
from apps.articles.serializers import (
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionWriteSerializer,
    CommentCreateUpdateSerializer,
    CommentSerializer,
)


def _parse_vote_value(raw):
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value in (1, -1) else None


def _apply_vote(vote_model, lookup, value):
    '''Create/update/toggle-off a vote; returns the resulting user_vote (None if removed).'''
    existing = vote_model.objects.filter(**lookup).first()
    if existing and existing.value == value:
        existing.delete()
        return None
    if existing:
        existing.value = value
        existing.save(update_fields=['value'])
        return value
    vote_model.objects.create(value=value, **lookup)
    return value


class QuestionViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['title', 'content']

    def get_queryset(self):
        queryset = Question.objects.select_related('author', 'category')

        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        category = self.request.query_params.get('category')
        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=category)
            else:
                queryset = queryset.filter(category__slug=category)

        if self.request.query_params.get('unresolved') == 'true':
            queryset = queryset.filter(accepted_comment__isnull=True)

        # Forum tab filters: 'mine' (subjects I follow), 'popular' (by net votes),
        # 'unanswered' (zero answers), 'new' (default recency ordering).
        tab_filter = self.request.query_params.get('filter')
        if tab_filter == 'mine' and self.request.user.is_authenticated:
            queryset = queryset.filter(category__followers__user=self.request.user)
        elif tab_filter == 'unanswered':
            queryset = queryset.filter(comments__isnull=True)
        elif tab_filter == 'popular':
            queryset = queryset.annotate(
                _vote_score=Coalesce(Sum('votes__value'), 0)
            ).order_by('-_vote_score', '-created_at')

        return queryset.distinct()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'comments':
            return [IsAuthenticatedOrReadOnly()]
        if self.action in ['favorite', 'favorites', 'vote']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsQuestionAuthorOrAdminOrReadOnly()]

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return QuestionWriteSerializer
        return QuestionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # QuestionWriteSerializer has no author field — respond with the detail
        # representation so callers get the nested author back.
        response_serializer = QuestionDetailSerializer(serializer.instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self, request, slug=None):
        question = self.get_object()

        if request.method == 'GET':
            comments = question.comments.select_related('user').all()
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = CommentSerializer(page, many=True, context=self.get_serializer_context())
                return self.get_paginated_response(serializer.data)

            serializer = CommentSerializer(comments, many=True, context=self.get_serializer_context())
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CommentCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(question=question, user=request.user)
            # Return the created comment with full details
            response_serializer = CommentSerializer(comment, context=self.get_serializer_context())
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, slug=None):
        question = self.get_object()
        vote_value = _parse_vote_value(request.data.get('value'))
        if vote_value is None:
            return Response({'detail': 'value must be 1 or -1.'}, status=status.HTTP_400_BAD_REQUEST)

        user_vote = _apply_vote(QuestionVote, {'question': question, 'user': request.user}, vote_value)
        vote_score = question.votes.aggregate(total=Sum('value'))['total'] or 0
        return Response({'vote_score': vote_score, 'user_vote': user_vote})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, slug=None):
        question = self.get_object()
        favorite, created = FavoriteArticle.objects.get_or_create(user=request.user, question=question)
        if not created:
            favorite.delete()
        return Response({'favorited': created})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        '''List of questions the current user has favorited.'''
        questions = Question.objects.filter(
            favorited_by__user=request.user
        ).select_related('author', 'category').distinct()

        page = self.paginate_queryset(questions)
        if page is not None:
            serializer = QuestionListSerializer(page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

        serializer = QuestionListSerializer(questions, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept_answer(self, request, slug=None):
        question = self.get_object()
        
        # Only author can accept answers
        if question.author != request.user and not request.user.is_staff:
            return Response({"detail": "Only author can accept answers."}, status=status.HTTP_403_FORBIDDEN)
            
        comment_id = request.data.get('comment_id')
        if not comment_id:
            return Response({"detail": "comment_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            comment = question.comments.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
            
        question.accepted_comment = comment
        question.save()
        return Response({"detail": "Answer accepted."})


class CommentViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCommentOwnerOrAdminOrReadOnly]

    def get_permissions(self):
        if self.action == 'vote':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        comment = self.get_object()
        vote_value = _parse_vote_value(request.data.get('value'))
        if vote_value is None:
            return Response({'detail': 'value must be 1 or -1.'}, status=status.HTTP_400_BAD_REQUEST)

        user_vote = _apply_vote(CommentVote, {'comment': comment, 'user': request.user}, vote_value)
        vote_score = comment.votes.aggregate(total=Sum('value'))['total'] or 0
        return Response({'vote_score': vote_score, 'user_vote': user_vote})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full details for the updated comment
        response_serializer = CommentSerializer(instance)
        return Response(response_serializer.data)

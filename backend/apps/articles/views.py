# Third-party modules
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# Project modules
from apps.articles.models import Comment, FavoriteArticle, Question
from apps.articles.permissions import IsCommentOwnerOrAdminOrReadOnly, IsQuestionAuthorOrAdminOrReadOnly
from apps.articles.serializers import (
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionWriteSerializer,
    CommentCreateUpdateSerializer,
    CommentSerializer,
)


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

        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'comments':
            return [IsAuthenticatedOrReadOnly()]
        if self.action in ['favorite', 'favorites']:
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
                serializer = CommentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CommentCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(question=question, user=request.user)
            # Return the created comment with full details
            response_serializer = CommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full details for the updated comment
        response_serializer = CommentSerializer(instance)
        return Response(response_serializer.data)

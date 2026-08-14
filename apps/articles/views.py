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


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('author').all()
    lookup_field = 'slug'
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_fields = ['category']

    # Add SessionAuthentication so the temporary HTML frontend works with Admin login
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'comments':
            return [IsAuthenticatedOrReadOnly()]
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


class CommentViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCommentOwnerOrAdminOrReadOnly]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full details for the updated comment
        response_serializer = CommentSerializer(instance)
        return Response(response_serializer.data)

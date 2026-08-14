# Third-party modules
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# Project modules
from apps.articles.models import Article, ArticleBlock, Comment, FavoriteArticle
from apps.articles.permissions import IsArticleAuthorOrAdminOrReadOnly, IsCommentOwnerOrAdminOrReadOnly
from apps.articles.serializers import (
    ArticleBlockSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    ArticleWriteSerializer,
    CommentCreateUpdateSerializer,
    CommentSerializer,
)


from django_filters.rest_framework import DjangoFilterBackend

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('author').all()
    lookup_field = 'slug'
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_fields = ['category']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'comments':
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated(), IsArticleAuthorOrAdminOrReadOnly()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ArticleWriteSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self, request, slug=None):
        article = self.get_object()

        if request.method == 'GET':
            comments = article.comments.select_related('user').all()
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = CommentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CommentCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(article=article, user=request.user)
            # Return the created comment with full details
            response_serializer = CommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, slug=None):
        article = self.get_object()
        favorite, created = FavoriteArticle.objects.get_or_create(user=request.user, article=article)
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full details for the updated comment
        response_serializer = CommentSerializer(instance)
        return Response(response_serializer.data)


class ArticleBlockViewSet(viewsets.ModelViewSet):
    queryset = ArticleBlock.objects.all()
    serializer_class = ArticleBlockSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        article_id = self.request.data.get('article')
        # Validate that the user is the author of the article
        article = Article.objects.get(id=article_id)
        if article.author != self.request.user:
            raise PermissionDenied("You can only add blocks to your own articles.")
        serializer.save(article=article)

    def perform_update(self, serializer):
        if serializer.instance.article.author != self.request.user:
            raise PermissionDenied("You can only edit blocks in your own articles.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.article.author != self.request.user:
            raise PermissionDenied("You can only delete blocks in your own articles.")
        instance.delete()

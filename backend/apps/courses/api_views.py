# Django modules
from django.db.models import Q

# Third-party modules
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# Project modules
from apps.common.permissions import IsAuthorOrReadOnly
from apps.courses.models import Category, Course, Favorite, Material, Rating
from apps.courses.permissions import IsRatingOwnerOrAdminOrReadOnly
from apps.courses.serializers import (
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
    MaterialSerializer,
    RatingSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        '''Anyone sees published courses; authenticated users also see their own drafts.'''
        queryset = Course.objects.select_related('category', 'author')
        user = self.request.user

        if user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(author=user))
        else:
            queryset = queryset.filter(is_published=True)

        category = self.request.query_params.get('category')
        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=category)
            else:
                queryset = queryset.filter(category__slug=category)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CourseWriteSerializer
        return CourseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def materials(self, request, pk=None):
        '''Author-only: attach a PDF or video-link material to this course.'''
        course = self.get_object()

        serializer = MaterialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        '''Toggle the current user's favorite on this course.'''
        course = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, course=course)
        if not created:
            favorite.delete()
        return Response({'favorited': created})

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def ratings(self, request, pk=None):
        '''List a course's reviews, or leave/update your own (one per user per course).'''
        course = self.get_object()

        if request.method == 'GET':
            ratings = course.ratings.select_related('user')
            page = self.paginate_queryset(ratings)
            if page is not None:
                serializer = RatingSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = RatingSerializer(ratings, many=True)
            return Response(serializer.data)

        if course.author == request.user:
            raise PermissionDenied("You can't rate your own course.")

        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating, _ = Rating.objects.update_or_create(
            course=course,
            user=request.user,
            defaults=serializer.validated_data,
        )
        response_serializer = RatingSerializer(rating)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MaterialViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    '''Retrieve/update/delete a single material; creation happens via CourseViewSet.materials().'''

    queryset = Material.objects.select_related('course__author')
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class RatingViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    '''Retrieve/update/delete a single rating; creation happens via CourseViewSet.ratings().'''

    queryset = Rating.objects.select_related('course', 'user')
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRatingOwnerOrAdminOrReadOnly]

# Django modules
from django.db.models import Max, Q

# Third-party modules
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# Project modules
from apps.common.permissions import IsAuthorOrReadOnly
from apps.courses.models import Category, CategoryFollow, ContentBlock, Course, Favorite, LessonProgress, Rating, Resource, Section
from apps.courses.permissions import IsRatingOwnerOrAdminOrReadOnly
from apps.courses.serializers import (
    CategorySerializer,
    ContentBlockSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
    RatingSerializer,
    ResourceSerializer,
    ResourceWriteSerializer,
    SectionSerializer,
    SubjectDetailSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    '''The catalog/forum "category" filter list, and — via retrieve — a subject's hub page.'''

    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from django.db.models import Count, Q as _Q
        queryset = Category.objects.annotate(
            course_count=Count('courses', filter=_Q(courses__is_published=True), distinct=True)
        ).order_by('-course_count')

        if self.request.query_params.get('following') == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(followers__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        return CategorySerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        '''Toggle the current user's subscription to this subject.'''
        category = self.get_object()
        follow, created = CategoryFollow.objects.get_or_create(user=request.user, category=category)
        if not created:
            follow.delete()
        return Response({'following': created})


class ResourceViewSet(viewsets.ModelViewSet):
    '''Loose, subject-scoped materials (PDFs, notes, cheat sheets, links, videos).'''

    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        queryset = Resource.objects.select_related('category', 'author')
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ResourceWriteSerializer
        return ResourceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)

        response_serializer = ResourceSerializer(serializer.instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        '''Anyone sees published courses; authenticated users also see their own drafts.'''
        queryset = Course.objects.select_related('category', 'author').prefetch_related('ratings', 'sections', 'sections__blocks')
        user = self.request.user
        if self.action == 'list':
            author_id = self.request.query_params.get('author')
            public_only = self.request.query_params.get('public_only') == 'true'

            if author_id:
                queryset = queryset.filter(author_id=author_id)
                if not public_only and user.is_authenticated and str(user.id) == str(author_id):
                    pass # Can see own drafts
                else:
                    queryset = queryset.filter(is_published=True)
            else:
                queryset = queryset.filter(is_published=True)
        else:
            if user.is_authenticated:
                queryset = queryset.filter(Q(is_published=True) | Q(author=user))
            else:
                queryset = queryset.filter(is_published=True)

        categories_param = self.request.query_params.get('categories')
        if categories_param:
            categories_list = categories_param.split(',')
            category_ids = [c for c in categories_list if c.isdigit()]
            category_slugs = [c for c in categories_list if not c.isdigit()]
            
            q_objects = Q()
            if category_ids:
                q_objects |= Q(category_id__in=category_ids)
            if category_slugs:
                q_objects |= Q(category__slug__in=category_slugs)
            
            if q_objects:
                queryset = queryset.filter(q_objects)
        else:
            category = self.request.query_params.get('category')
            if category:
                if category.isdigit():
                    queryset = queryset.filter(category_id=category)
                else:
                    queryset = queryset.filter(category__slug=category)
        min_rating = self.request.query_params.get('min_rating')
        sort_param = self.request.query_params.get('sort')
        
        if min_rating or sort_param in ['rating_asc', 'rating_desc']:
            from django.db.models import Avg
            queryset = queryset.annotate(avg_rating=Avg('ratings__score'))
            
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=float(min_rating))

        # Full-Text Search replacement
        search_query = self.request.query_params.get('search')
        if search_query:
            from django.contrib.postgres.search import SearchVector, TrigramSimilarity
            # Using TrigramSimilarity for better partial matches and SearchVector for FTS
            queryset = queryset.annotate(
                search=SearchVector('title', 'description'),
                similarity=TrigramSimilarity('title', search_query)
            ).filter(
                Q(search=search_query) | Q(similarity__gt=0.1)
            ).order_by('-similarity')
            
        if sort_param == 'rating_asc':
            queryset = queryset.order_by('avg_rating')
        elif sort_param == 'rating_desc':
            queryset = queryset.order_by('-avg_rating')

        # 'Continue Learning': courses the user has made any progress in,
        # most recently-touched first.
        if self.request.query_params.get('filter') == 'in_progress' and user.is_authenticated:
            queryset = queryset.filter(sections__blocks__completions__user=user).annotate(
                last_progress_at=Max('sections__blocks__completions__created_at')
            ).order_by('-last_progress_at')

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
    def sections(self, request, pk=None):
        '''Author-only: create a new section in this course.'''
        course = self.get_object()

        serializer = SectionSerializer(data=request.data)
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


class SectionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    '''Retrieve/update/delete a section; creation happens via CourseViewSet.sections().'''

    queryset = Section.objects.select_related('course__author')
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    @action(detail=True, methods=['post'])
    def blocks(self, request, pk=None):
        '''Author-only: attach a content block to this section.'''
        section = self.get_object()
        # Verify user is author of the course
        if section.course.author != request.user:
            raise PermissionDenied("Only the course author can add blocks.")

        serializer = ContentBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(section=section)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContentBlockViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    '''Retrieve/update/delete a content block; creation happens via SectionViewSet.blocks().'''

    queryset = ContentBlock.objects.select_related('section__course__author')
    serializer_class = ContentBlockSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Ideally IsAuthorOrReadOnly but we'd need to adapt permission class to check section.course.author

    def perform_update(self, serializer):
        if serializer.instance.section.course.author != self.request.user:
            raise PermissionDenied("Only the course author can update this block.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.section.course.author != self.request.user:
            raise PermissionDenied("Only the course author can delete this block.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        '''Toggle the current user's completion mark on this lesson.'''
        block = self.get_object()
        progress, created = LessonProgress.objects.get_or_create(user=request.user, block=block)
        if not created:
            progress.delete()
        return Response({'completed': created})


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

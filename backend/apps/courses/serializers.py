import logging

# Third-party modules
from rest_framework import serializers

logger = logging.getLogger(__name__)

# Project modules
from apps.common.serializers import AuthorSerializer
from apps.courses.models import Category, ContentBlock, Course, Rating, Resource, Section

MAX_PDF_SIZE_MB = 10
MAX_COVER_SIZE_MB = 5


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'code', 'course_count']
        read_only_fields = ['slug', 'course_count']


class SubjectDetailSerializer(serializers.ModelSerializer):
    '''Category, dressed up with the stats/actions a Subject hub page needs.

    Kept separate from CategorySerializer so the catalog/forum filter-chip
    endpoints stay exactly as cheap as they were.
    '''

    students_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    guides_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'code', 'description',
            'students_count', 'materials_count', 'guides_count', 'questions_count', 'is_following',
        ]

    def get_students_count(self, obj) -> int:
        # No enrollment concept exists yet; subscriber count doubles as "students" for now.
        return obj.followers.count()

    def get_materials_count(self, obj) -> int:
        return obj.resources.count()

    def get_guides_count(self, obj) -> int:
        return obj.courses.filter(is_published=True).count()

    def get_questions_count(self, obj) -> int:
        return obj.questions.count()

    def get_is_following(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.followers.filter(user=request.user).exists()


class ResourceSerializer(serializers.ModelSerializer):
    '''Read shape — nested category/author, matching CourseListSerializer's convention.'''

    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Resource
        fields = ['id', 'category', 'author', 'title', 'type', 'url', 'file', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class ResourceWriteSerializer(serializers.ModelSerializer):
    '''Create/update shape — plain category id, so it's actually writable (see CourseWriteSerializer).'''

    class Meta:
        model = Resource
        fields = ['id', 'category', 'title', 'type', 'url', 'file']
        read_only_fields = ['id']

    def validate(self, attrs):
        resource_type = attrs.get('type')
        url = attrs.get('url')
        file = attrs.get('file')

        if resource_type in (Resource.ResourceType.LINK, Resource.ResourceType.VIDEO) and not url:
            raise serializers.ValidationError({'url': 'This resource type needs a URL.'})
        if resource_type in (Resource.ResourceType.PDF, Resource.ResourceType.NOTES,
                              Resource.ResourceType.CHEATSHEET, Resource.ResourceType.PAST_PAPER) and not file:
            raise serializers.ValidationError({'file': 'This resource type needs a file.'})
        return attrs


class ContentBlockSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = ContentBlock
        fields = ['id', 'section', 'title', 'type', 'content', 'file', 'order', 'created_at', 'is_completed']
        read_only_fields = ['id', 'section', 'created_at']

    def get_is_completed(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.completions.filter(user=request.user).exists()

    def validate(self, attrs):
        block_type = attrs.get('type', getattr(self.instance, 'type', None))
        file = attrs.get('file', getattr(self.instance, 'file', None))

        if block_type == ContentBlock.BlockType.MEDIA:
            if file and file.size > MAX_PDF_SIZE_MB * 1024 * 1024:
                raise serializers.ValidationError(
                    {'file': f'File must be smaller than {MAX_PDF_SIZE_MB}MB.'}
                )
        return attrs


class SectionSerializer(serializers.ModelSerializer):
    blocks = ContentBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'order', 'blocks', 'created_at']
        read_only_fields = ['id', 'course', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'course', 'user', 'score', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'course', 'user', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover', 'category', 'author', 'is_published', 'average_rating', 'ratings_count', 'created_at']

    def get_average_rating(self, obj):
        scores = [rating.score for rating in obj.ratings.all()]
        return round(sum(scores) / len(scores), 2) if scores else None

    def get_ratings_count(self, obj):
        return len(obj.ratings.all())


class CourseDetailSerializer(CourseListSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            'updated_at', 'sections', 'ratings'
        ]


class CourseWriteSerializer(serializers.ModelSerializer):
    '''Create/update fields only; excludes author so it can't be spoofed by the client.'''
    sections_data = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover', 'category', 'is_published', 'sections_data']
        read_only_fields = ['id']

    def validate_cover(self, value):
        if value and value.size > MAX_COVER_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f'Cover image must be smaller than {MAX_COVER_SIZE_MB}MB.')
        return value

    def create(self, validated_data):
        sections_data = validated_data.pop('sections_data', None)
        course = super().create(validated_data)

        if sections_data:
            import json
            try:
                if isinstance(sections_data, str):
                    sections_list = json.loads(sections_data)
                else:
                    sections_list = sections_data
                for s_idx, section_dict in enumerate(sections_list):
                    section = Section.objects.create(
                        course=course,
                        title=section_dict.get('title', f'Модуль {s_idx + 1}'),
                        order=s_idx
                    )
                    blocks = section_dict.get('blocks', [])
                    for b_idx, block_dict in enumerate(blocks):
                        block = ContentBlock.objects.create(
                            section=section,
                            type=block_dict.get('type', 'text'),
                            content=block_dict.get('content', ''),
                            order=b_idx
                        )
                        file_key = f'file_{s_idx}_{b_idx}'
                        if 'request' in self.context:
                            request_files = self.context['request'].FILES
                            if file_key in request_files:
                                block.file = request_files[file_key]
                                block.save()
            except Exception:
                logger.error("Error creating course structure", exc_info=True)
        return course

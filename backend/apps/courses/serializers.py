import logging

# Third-party modules
from rest_framework import serializers

logger = logging.getLogger(__name__)

# Project modules
from apps.common.serializers import AuthorSerializer
from apps.courses.models import Category, ContentBlock, Course, Rating, Section

MAX_PDF_SIZE_MB = 10
MAX_COVER_SIZE_MB = 5


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'course_count']
        read_only_fields = ['slug', 'course_count']


class ContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlock
        fields = ['id', 'section', 'type', 'content', 'file', 'order', 'created_at']
        read_only_fields = ['id', 'section', 'created_at']

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

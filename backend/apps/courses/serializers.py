# Third-party modules
from rest_framework import serializers

# Project modules
from apps.common.serializers import AuthorSerializer
from apps.courses.models import Category, Course, Lesson, Material, Rating

MAX_PDF_SIZE_MB = 10
MAX_COVER_SIZE_MB = 5


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'course_count']
        read_only_fields = ['slug', 'course_count']


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'course', 'lesson', 'title', 'type', 'file', 'url', 'content', 'order', 'created_at']
        read_only_fields = ['id', 'course', 'lesson', 'created_at']

    def validate(self, attrs):
        '''Enforce that each material type carries exactly the fields it needs.'''
        material_type = attrs.get('type', getattr(self.instance, 'type', None))
        file = attrs.get('file', getattr(self.instance, 'file', None))
        url = attrs.get('url', getattr(self.instance, 'url', None))
        content = attrs.get('content', getattr(self.instance, 'content', None))

        if material_type == Material.MaterialType.PDF:
            if not file:
                raise serializers.ValidationError(
                    {'file': 'PDF material must have a file attached.'}
                )
            if url:
                raise serializers.ValidationError({'url': 'PDF material must not have a URL.'})
            if not file.name.lower().endswith('.pdf'):
                raise serializers.ValidationError({'file': 'Only PDF files are allowed.'})
            if getattr(file, 'content_type', None) != 'application/pdf':
                raise serializers.ValidationError(
                    {'file': 'Uploaded file must be a PDF (application/pdf).'}
                )
            if file.size > MAX_PDF_SIZE_MB * 1024 * 1024:
                raise serializers.ValidationError(
                    {'file': f'File must be smaller than {MAX_PDF_SIZE_MB}MB.'}
                )
        elif material_type in (Material.MaterialType.VIDEO_LINK, Material.MaterialType.LINK):
            if not url:
                raise serializers.ValidationError({'url': 'This material must have a URL.'})
            if file:
                raise serializers.ValidationError(
                    {'file': 'This material must not have a file.'}
                )
        elif material_type == Material.MaterialType.TEXT:
            if not content:
                raise serializers.ValidationError({'content': 'Text material must have content.'})

        return attrs


class LessonSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order', 'materials', 'created_at']
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
        fields = [
            'id', 'title', 'description', 'cover', 'category', 'author',
            'is_published', 'average_rating', 'ratings_count', 'created_at',
        ]

    def get_average_rating(self, obj):
        scores = [rating.score for rating in obj.ratings.all()]
        return round(sum(scores) / len(scores), 2) if scores else None

    def get_ratings_count(self, obj):
        return len(obj.ratings.all())


class CourseDetailSerializer(CourseListSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    materials = serializers.SerializerMethodField()
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            'updated_at', 'lessons', 'materials', 'ratings',
        ]

    def get_materials(self, obj):
        '''Materials not grouped under any lesson (kept for backwards compatibility).'''
        ungrouped = obj.materials.filter(lesson__isnull=True)
        return MaterialSerializer(ungrouped, many=True).data


class CourseWriteSerializer(serializers.ModelSerializer):
    '''Create/update fields only; excludes author so it can't be spoofed by the client.'''

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover', 'category', 'is_published']
        read_only_fields = ['id']

    def validate_cover(self, value):
        if value and value.size > MAX_COVER_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f'Cover image must be smaller than {MAX_COVER_SIZE_MB}MB.')
        return value

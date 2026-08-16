# Third-party modules
from rest_framework import serializers

# Project modules
from apps.common.serializers import AuthorSerializer
from apps.courses.models import Category, Course, Material, Rating

MAX_PDF_SIZE_MB = 10
MAX_COVER_SIZE_MB = 5


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'course', 'title', 'type', 'file', 'url', 'order', 'created_at']
        read_only_fields = ['id', 'course', 'created_at']

    def validate(self, attrs):
        '''Enforce that pdf/video_link materials carry exactly the fields they need.'''
        material_type = attrs.get('type', getattr(self.instance, 'type', None))
        file = attrs.get('file', getattr(self.instance, 'file', None))
        url = attrs.get('url', getattr(self.instance, 'url', None))

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
        elif material_type == Material.MaterialType.VIDEO_LINK:
            if not url:
                raise serializers.ValidationError({'url': 'Video link material must have a URL.'})
            if file:
                raise serializers.ValidationError(
                    {'file': 'Video link material must not have a file.'}
                )

        return attrs


class RatingSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'course', 'user', 'score', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'course', 'user', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover', 'category', 'author', 'is_published', 'created_at']


class CourseDetailSerializer(CourseListSerializer):
    materials = MaterialSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            'updated_at', 'materials', 'ratings', 'average_rating', 'ratings_count'
        ]

    def get_average_rating(self, obj):
        scores = [rating.score for rating in obj.ratings.all()]
        return round(sum(scores) / len(scores), 2) if scores else None

    def get_ratings_count(self, obj):
        return obj.ratings.count()


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

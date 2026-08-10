from rest_framework import serializers

from apps.common.serializers import AuthorSerializer
from apps.courses.models import Category, Course, Material

MAX_PDF_SIZE_MB = 10


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = ["slug"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "course", "title", "type", "file", "url", "order", "created_at"]
        read_only_fields = ["id", "course", "created_at"]

    def validate(self, attrs):
        material_type = attrs.get("type", getattr(self.instance, "type", None))
        file = attrs.get("file", getattr(self.instance, "file", None))
        url = attrs.get("url", getattr(self.instance, "url", None))

        if material_type == Material.MaterialType.PDF:
            if not file:
                raise serializers.ValidationError({"file": "PDF material must have a file attached."})
            if url:
                raise serializers.ValidationError({"url": "PDF material must not have a URL."})
            if not file.name.lower().endswith(".pdf"):
                raise serializers.ValidationError({"file": "Only PDF files are allowed."})
            if file.size > MAX_PDF_SIZE_MB * 1024 * 1024:
                raise serializers.ValidationError({"file": f"File must be smaller than {MAX_PDF_SIZE_MB}MB."})
        elif material_type == Material.MaterialType.VIDEO_LINK:
            if not url:
                raise serializers.ValidationError({"url": "Video link material must have a URL."})
            if file:
                raise serializers.ValidationError({"file": "Video link material must not have a file."})

        return attrs


class CourseListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "author", "is_published", "created_at"]


class CourseDetailSerializer(CourseListSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ["updated_at", "materials"]


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "is_published"]
        read_only_fields = ["id"]

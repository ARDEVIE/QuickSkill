from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Allows write access only to the object's author (or its course's author)."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        author = getattr(obj, "author", None)
        if author is None:
            author = getattr(obj.course, "author", None)

        return author == request.user

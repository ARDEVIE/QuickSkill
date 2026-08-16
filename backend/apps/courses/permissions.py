# Third-party modules
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsRatingOwnerOrAdminOrReadOnly(BasePermission):
    '''Allows write access only to the rating's own author or admin.'''

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_admin or obj.user == request.user

# Third-party modules
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsQuestionAuthorOrAdminOrReadOnly(BasePermission):
    '''Allows write access only to the question's author or admin.'''

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
            
        return request.user.is_admin or obj.author == request.user


class IsCommentOwnerOrAdminOrReadOnly(BasePermission):
    '''Allows write access only to the comment's user or admin.'''

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
            
        return request.user.is_admin or obj.user == request.user

# Third-party modules
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from apps.users.models import CustomUser
from apps.users.serializers import PublicUserSerializer, RegisterSerializer, UserSerializer


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPublicProfileAPIView(generics.RetrieveAPIView):
    '''Public profile lookup by username — no email or other private fields exposed.'''

    queryset = CustomUser.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        '''Blacklist the given refresh token so it can no longer be used.'''
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'refresh': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {'refresh': ['Invalid or expired token.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

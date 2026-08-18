# Django modules
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Third-party modules
from rest_framework import generics, permissions, status
from rest_framework.response import Response

# Project modules
from apps.users.models import CustomUser
from apps.users.password_reset_serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

class PasswordResetRequestAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_active:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Typically send email here, for now print for dev
            reset_url = f"http://localhost:4200/reset-password?uid={uidb64}&token={token}"
            print(f"Password reset link for {email}: {reset_url}")
            
        # Always return 200 OK to prevent user enumeration
        return Response(
            {"detail": "If an account with this email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

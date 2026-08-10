from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models import (
    CASCADE,
    OneToOneField,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ImageField,
    TextChoices,
    TextField,
    Model,
)
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", CustomUser.Roles.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Roles(TextChoices):
        USER = "user", "User"
        MODERATOR = "moderator", "Moderator"
        ADMIN = "admin", "Admin"

    email = EmailField(unique=True)
    username = CharField(max_length=150, unique=True)
    first_name = CharField(max_length=150, blank=True)
    last_name = CharField(max_length=150, blank=True)
    telegram_username = CharField(max_length=64, blank=True)
    avatar = ImageField(upload_to="avatars/", blank=True, null=True)
    bio = TextField(blank=True)
    role = CharField(max_length=20, choices=Roles.choices, default=Roles.USER)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    @property
    def is_admin(self) -> bool:
        return self.role == self.Roles.ADMIN

    @property
    def is_moderator(self) -> bool:
        return self.role == self.Roles.MODERATOR

    @property
    def is_author(self) -> bool:
        """True once the user has published at least one course."""
        return self.authored_courses.exists()


class UserSettings(Model):
    class ThemeChoices(TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"

    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name="settings")
    theme = CharField(max_length=20, choices=ThemeChoices.choices, default=ThemeChoices.LIGHT)
    is_private = BooleanField(default=False)
    notifications_enabled = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"

    class Meta:
        verbose_name = "User settings"
        verbose_name_plural = "User settings"
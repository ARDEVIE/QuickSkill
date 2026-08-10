# Django modules
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

# Project modules
from apps.users.models import CustomUser, UserSettings


class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )


class UserProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'telegram_username',
            'avatar',
            'bio',
        )

    def clean_telegram_username(self):
        username = self.cleaned_data['telegram_username']
        return username.strip().lstrip('@')


class UserSettingsForm(ModelForm):
    class Meta:
        model = UserSettings
        fields = (
            'theme',
            'is_private',
            'notifications_enabled',
        )

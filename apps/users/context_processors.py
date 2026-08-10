# Project modules
from apps.users.models import UserSettings


def theme(request):
    '''Expose the current user's theme (or the default) to every template.'''
    default_theme = UserSettings.ThemeChoices.LIGHT

    if not request.user.is_authenticated:
        return {'active_theme': default_theme}

    try:
        return {'active_theme': request.user.settings.theme}
    except UserSettings.DoesNotExist:
        return {'active_theme': default_theme}

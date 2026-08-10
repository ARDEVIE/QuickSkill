# Django modules
from django.forms import ModelForm

# Project modules
from apps.courses.models import Course, Material


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'is_published']


class MaterialForm(ModelForm):
    '''Model-level Material.clean() runs automatically and enforces pdf/video_link rules.'''

    class Meta:
        model = Material
        fields = ['title', 'type', 'file', 'url', 'order']

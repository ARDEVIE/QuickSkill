# Python modules
import base64

# Django modules
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

# Third-party modules
from rest_framework import status
from rest_framework.test import APITestCase

# Project modules
from apps.courses.models import Category, Course, Favorite, Lesson, Material, Rating

User = get_user_model()

# 1x1 transparent PNG — the smallest valid image Pillow will accept for an ImageField.
TINY_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
)


def create_user(**extra_fields):
    data = {
        'email': 'user@example.com',
        'username': 'user',
        'password': 'StrongPassword123!',
    }
    data.update(extra_fields)
    return User.objects.create_user(**data)


class CategoryModelTests(TestCase):
    def test_slug_is_generated_from_name(self):
        category = Category.objects.create(name='Web Development')
        self.assertEqual(category.slug, 'web-development')

    def test_explicit_slug_is_kept(self):
        category = Category.objects.create(name='Python', slug='custom-slug')
        self.assertEqual(category.slug, 'custom-slug')

    def test_slug_keeps_cyrillic_instead_of_going_blank(self):
        category = Category.objects.create(name='Вёрстка')
        self.assertEqual(category.slug, 'вёрстка')


class MaterialModelTests(TestCase):
    def setUp(self):
        self.author = create_user()
        self.course = Course.objects.create(title='Django basics', author=self.author)

    def test_pdf_without_file_is_invalid(self):
        material = Material(course=self.course, title='Slides', type=Material.MaterialType.PDF)
        with self.assertRaises(ValidationError):
            material.clean()

    def test_pdf_with_url_is_invalid(self):
        material = Material(
            course=self.course,
            title='Slides',
            type=Material.MaterialType.PDF,
            file=SimpleUploadedFile('slides.pdf', b'%PDF-1.4 fake', content_type='application/pdf'),
            url='https://example.com/video',
        )
        with self.assertRaises(ValidationError):
            material.clean()

    def test_video_link_without_url_is_invalid(self):
        material = Material(
            course=self.course, title='Lecture', type=Material.MaterialType.VIDEO_LINK
        )
        with self.assertRaises(ValidationError):
            material.clean()

    def test_video_link_with_file_is_invalid(self):
        material = Material(
            course=self.course,
            title='Lecture',
            type=Material.MaterialType.VIDEO_LINK,
            url='https://example.com/video',
            file=SimpleUploadedFile('slides.pdf', b'%PDF-1.4 fake', content_type='application/pdf'),
        )
        with self.assertRaises(ValidationError):
            material.clean()

    def test_valid_video_link_passes_clean(self):
        material = Material(
            course=self.course,
            title='Lecture',
            type=Material.MaterialType.VIDEO_LINK,
            url='https://example.com/video',
        )
        material.clean()  # should not raise

    def test_link_without_url_is_invalid(self):
        material = Material(course=self.course, title='Docs', type=Material.MaterialType.LINK)
        with self.assertRaises(ValidationError):
            material.clean()

    def test_text_without_content_is_invalid(self):
        material = Material(course=self.course, title='Notes', type=Material.MaterialType.TEXT)
        with self.assertRaises(ValidationError):
            material.clean()

    def test_valid_text_passes_clean(self):
        material = Material(
            course=self.course, title='Notes', type=Material.MaterialType.TEXT, content='Hello'
        )
        material.clean()  # should not raise


class FavoriteModelTests(TestCase):
    def test_same_user_cannot_favorite_same_course_twice(self):
        author = create_user()
        fan = create_user(email='fan@example.com', username='fan')
        course = Course.objects.create(title='Django basics', author=author)

        Favorite.objects.create(user=fan, course=course)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Favorite.objects.create(user=fan, course=course)


class RatingModelTests(TestCase):
    def test_same_user_cannot_rate_same_course_twice(self):
        author = create_user()
        fan = create_user(email='fan@example.com', username='fan')
        course = Course.objects.create(title='Django basics', author=author)

        Rating.objects.create(user=fan, course=course, score=5)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Rating.objects.create(user=fan, course=course, score=3)


class CourseCatalogAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')
        self.other = create_user(email='other@example.com', username='other')
        self.category = Category.objects.create(name='Python')

        self.published = Course.objects.create(
            title='Django for beginners',
            category=self.category,
            author=self.author,
            is_published=True,
        )
        self.draft = Course.objects.create(
            title='Advanced Django (draft)',
            category=self.category,
            author=self.author,
            is_published=False,
        )

    def test_anonymous_sees_only_published_courses(self):
        response = self.client.get(reverse('course-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.published.id, ids)
        self.assertNotIn(self.draft.id, ids)

    def test_author_sees_own_drafts_too(self):
        self.client.force_authenticate(self.author)
        response = self.client.get(reverse('course-list'))

        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.published.id, ids)
        self.assertIn(self.draft.id, ids)

    def test_other_user_does_not_see_someone_elses_draft(self):
        self.client.force_authenticate(self.other)
        response = self.client.get(reverse('course-list'))

        ids = [item['id'] for item in response.data['results']]
        self.assertNotIn(self.draft.id, ids)

    def test_search_by_title(self):
        response = self.client.get(reverse('course-list'), {'search': 'beginners'})

        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.published.id])

    def test_filter_by_category_slug(self):
        other_category = Category.objects.create(name='Design')
        Course.objects.create(
            title='UI basics',
            category=other_category,
            author=self.author,
            is_published=True,
        )

        response = self.client.get(reverse('course-list'), {'category': self.category.slug})

        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.published.id])

    def test_pagination_response_shape(self):
        response = self.client.get(reverse('course-list'))

        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

    def test_course_detail_exposes_author_telegram_link(self):
        self.author.telegram_username = 'ualikhan'
        self.author.save(update_fields=['telegram_username'])

        response = self.client.get(reverse('course-detail', args=[self.published.id]))

        self.assertEqual(response.data['author']['telegram_url'], 'https://t.me/ualikhan')

    def test_course_detail_telegram_link_is_none_when_not_set(self):
        response = self.client.get(reverse('course-detail', args=[self.published.id]))
        self.assertIsNone(response.data['author']['telegram_url'])


class CoursePermissionAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')
        self.other = create_user(email='other@example.com', username='other')
        self.category = Category.objects.create(name='Python')

    def test_create_course_requires_authentication(self):
        response = self.client.post(reverse('course-list'), {'title': 'New course'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_is_forced_from_request_user(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            reverse('course-list'),
            {'title': 'New course', 'description': 'desc', 'is_published': True},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(id=response.data['id'])
        self.assertEqual(course.author, self.author)

    def test_client_supplied_author_field_is_ignored(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            reverse('course-list'),
            {'title': 'New course', 'author': self.other.id},
        )

        course = Course.objects.get(id=response.data['id'])
        self.assertEqual(course.author, self.author)

    def test_non_author_cannot_update_course(self):
        course = Course.objects.create(
            title='Django basics', author=self.author, category=self.category, is_published=True
        )
        self.client.force_authenticate(self.other)

        response = self.client.patch(
            reverse('course-detail', args=[course.id]), {'title': 'Hacked'}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Django basics')

    def test_non_author_cannot_delete_course(self):
        course = Course.objects.create(
            title='Django basics', author=self.author, category=self.category, is_published=True
        )
        self.client.force_authenticate(self.other)

        response = self.client.delete(reverse('course-detail', args=[course.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(id=course.id).exists())

    def test_author_can_update_own_course(self):
        course = Course.objects.create(
            title='Django basics', author=self.author, category=self.category
        )
        self.client.force_authenticate(self.author)

        response = self.client.patch(
            reverse('course-detail', args=[course.id]), {'title': 'Updated title'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Updated title')

    def test_author_can_delete_own_course(self):
        course = Course.objects.create(
            title='Django basics', author=self.author, category=self.category
        )
        self.client.force_authenticate(self.author)

        response = self.client.delete(reverse('course-detail', args=[course.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())


class MaterialAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')
        self.other = create_user(email='other@example.com', username='other')
        self.course = Course.objects.create(
            title='Django basics', author=self.author, is_published=True
        )

    def test_author_can_add_video_link_material(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            reverse('course-materials', args=[self.course.id]),
            {'title': 'Lecture 1', 'type': 'video_link', 'url': 'https://example.com/video'},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.course.materials.count(), 1)

    def test_author_can_add_pdf_material(self):
        self.client.force_authenticate(self.author)
        pdf = SimpleUploadedFile(
            'slides.pdf', b'%PDF-1.4 fake pdf content', content_type='application/pdf'
        )

        response = self.client.post(
            reverse('course-materials', args=[self.course.id]),
            {'title': 'Slides', 'type': 'pdf', 'file': pdf},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        material = Material.objects.get(id=response.data['id'])
        self.assertTrue(material.file.name.endswith('.pdf'))

    def test_pdf_material_rejects_non_pdf_extension(self):
        self.client.force_authenticate(self.author)
        fake_file = SimpleUploadedFile('notes.txt', b'just text', content_type='text/plain')

        response = self.client.post(
            reverse('course-materials', args=[self.course.id]),
            {'title': 'Notes', 'type': 'pdf', 'file': fake_file},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_author_cannot_add_material(self):
        self.client.force_authenticate(self.other)
        response = self.client.post(
            reverse('course-materials', args=[self.course.id]),
            {'title': 'Lecture 1', 'type': 'video_link', 'url': 'https://example.com/video'},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_author_cannot_delete_material(self):
        material = Material.objects.create(
            course=self.course,
            title='Lecture 1',
            type=Material.MaterialType.VIDEO_LINK,
            url='https://example.com/video',
        )
        self.client.force_authenticate(self.other)

        response = self.client.delete(reverse('material-detail', args=[material.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_material(self):
        material = Material.objects.create(
            course=self.course,
            title='Lecture 1',
            type=Material.MaterialType.VIDEO_LINK,
            url='https://example.com/video',
        )
        self.client.force_authenticate(self.author)

        response = self.client.delete(reverse('material-detail', args=[material.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class LessonAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')
        self.other = create_user(email='other@example.com', username='other')
        self.course = Course.objects.create(
            title='Django basics', author=self.author, is_published=True
        )

    def test_author_can_create_lesson(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            reverse('course-lessons', args=[self.course.id]),
            {'title': 'Introduction', 'description': 'First topic'},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.course.lessons.count(), 1)

    def test_non_author_cannot_create_lesson(self):
        self.client.force_authenticate(self.other)
        response = self.client.post(
            reverse('course-lessons', args=[self.course.id]), {'title': 'Introduction'}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_add_link_and_text_material_to_lesson(self):
        self.client.force_authenticate(self.author)
        lesson = Lesson.objects.create(course=self.course, title='Introduction')

        link_response = self.client.post(
            reverse('lesson-materials', args=[lesson.id]),
            {'title': 'Docs', 'type': 'link', 'url': 'https://example.com'},
        )
        text_response = self.client.post(
            reverse('lesson-materials', args=[lesson.id]),
            {'title': 'Notes', 'type': 'text', 'content': 'Some notes'},
        )

        self.assertEqual(link_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(text_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(lesson.materials.count(), 2)

    def test_course_detail_groups_materials_by_lesson(self):
        lesson = Lesson.objects.create(course=self.course, title='Introduction')
        Material.objects.create(
            course=self.course, lesson=lesson, title='Video', type=Material.MaterialType.VIDEO_LINK,
            url='https://example.com/video',
        )
        Material.objects.create(
            course=self.course, title='Ungrouped link', type=Material.MaterialType.LINK,
            url='https://example.com',
        )

        response = self.client.get(reverse('course-detail', args=[self.course.id]))

        self.assertEqual(len(response.data['lessons']), 1)
        self.assertEqual(len(response.data['lessons'][0]['materials']), 1)
        self.assertEqual(len(response.data['materials']), 1)


class FavoriteAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')
        self.fan = create_user(email='fan@example.com', username='fan')
        self.course = Course.objects.create(
            title='Django basics', author=self.author, is_published=True
        )

    def test_favorite_requires_authentication(self):
        response = self.client.post(reverse('course-favorite', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toggle_favorite_adds_then_removes(self):
        self.client.force_authenticate(self.fan)

        response = self.client.post(reverse('course-favorite', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['favorited'])
        self.assertTrue(Favorite.objects.filter(user=self.fan, course=self.course).exists())

        response = self.client.post(reverse('course-favorite', args=[self.course.id]))
        self.assertFalse(response.data['favorited'])
        self.assertFalse(Favorite.objects.filter(user=self.fan, course=self.course).exists())

    def test_favorites_list_requires_authentication(self):
        response = self.client.get(reverse('course-favorites'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorites_list_returns_only_favorited_courses(self):
        other_course = Course.objects.create(
            title='Not favorited', author=self.author, is_published=True
        )
        Favorite.objects.create(user=self.fan, course=self.course)
        self.client.force_authenticate(self.fan)

        response = self.client.get(reverse('course-favorites'))

        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.course.id, ids)
        self.assertNotIn(other_course.id, ids)


class CategoryAPITests(APITestCase):
    def test_list_categories_is_public(self):
        Category.objects.create(name='Python')
        Category.objects.create(name='Design')

        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_categories_are_read_only(self):
        response = self.client.post(reverse('category-list'), {'name': 'New category'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CourseCoverAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')

    def test_create_course_with_cover(self):
        self.client.force_authenticate(self.author)
        cover = SimpleUploadedFile('cover.png', TINY_PNG, content_type='image/png')

        response = self.client.post(
            reverse('course-list'),
            {'title': 'Django basics', 'cover': cover},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(id=response.data['id'])
        self.assertTrue(course.cover.name.startswith('courses/covers/cover'))

    def test_cover_is_optional(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(reverse('course-list'), {'title': 'Django basics'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_oversized_cover_is_rejected(self):
        self.client.force_authenticate(self.author)
        big_file = SimpleUploadedFile('cover.png', TINY_PNG + b'\0' * (6 * 1024 * 1024), content_type='image/png')

        response = self.client.post(
            reverse('course-list'),
            {'title': 'Django basics', 'cover': big_file},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cover', response.data)


class RatingAPITests(APITestCase):
    def setUp(self):
        self.author = create_user(email='author@example.com', username='author')
        self.fan = create_user(email='fan@example.com', username='fan')
        self.other_fan = create_user(email='other_fan@example.com', username='other_fan')
        self.course = Course.objects.create(
            title='Django basics', author=self.author, is_published=True
        )
        self.ratings_url = reverse('course-ratings', args=[self.course.id])

    def test_rating_requires_authentication(self):
        response = self.client.post(self.ratings_url, {'score': 5})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_cannot_rate_own_course(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(self.ratings_url, {'score': 5})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_rating(self):
        self.client.force_authenticate(self.fan)
        response = self.client.post(self.ratings_url, {'score': 4, 'comment': 'Solid intro course.'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'fan')
        self.assertTrue(Rating.objects.filter(user=self.fan, course=self.course, score=4).exists())

    def test_rating_again_updates_instead_of_duplicating(self):
        self.client.force_authenticate(self.fan)
        self.client.post(self.ratings_url, {'score': 2, 'comment': 'Meh.'})

        response = self.client.post(self.ratings_url, {'score': 5, 'comment': 'Actually great.'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.filter(user=self.fan, course=self.course).count(), 1)
        self.assertEqual(Rating.objects.get(user=self.fan, course=self.course).score, 5)

    def test_list_ratings_is_public(self):
        Rating.objects.create(user=self.fan, course=self.course, score=4)
        Rating.objects.create(user=self.other_fan, course=self.course, score=2)

        response = self.client.get(self.ratings_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_course_detail_exposes_average_and_count(self):
        Rating.objects.create(user=self.fan, course=self.course, score=4)
        Rating.objects.create(user=self.other_fan, course=self.course, score=2)

        response = self.client.get(reverse('course-detail', args=[self.course.id]))

        self.assertEqual(response.data['average_rating'], 3.0)
        self.assertEqual(response.data['ratings_count'], 2)

    def test_course_detail_average_is_none_without_ratings(self):
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertIsNone(response.data['average_rating'])
        self.assertEqual(response.data['ratings_count'], 0)

    def test_owner_can_update_own_rating(self):
        rating = Rating.objects.create(user=self.fan, course=self.course, score=3)
        self.client.force_authenticate(self.fan)

        response = self.client.patch(reverse('rating-detail', args=[rating.id]), {'score': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rating.refresh_from_db()
        self.assertEqual(rating.score, 5)

    def test_other_user_cannot_update_someone_elses_rating(self):
        rating = Rating.objects.create(user=self.fan, course=self.course, score=3)
        self.client.force_authenticate(self.other_fan)

        response = self.client.patch(reverse('rating-detail', args=[rating.id]), {'score': 1})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_own_rating(self):
        rating = Rating.objects.create(user=self.fan, course=self.course, score=3)
        self.client.force_authenticate(self.fan)

        response = self.client.delete(reverse('rating-detail', args=[rating.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rating.objects.filter(id=rating.id).exists())


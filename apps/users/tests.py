# Django modules
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Third-party modules
from rest_framework import status
from rest_framework.test import APITestCase

# Project modules
from apps.courses.models import Course


class CustomUserModelTests(TestCase):
    def test_is_author_is_false_until_user_creates_a_course(self):
        user = get_user_model().objects.create_user(
            email='user@example.com', username='user', password='StrongPassword123!'
        )
        self.assertFalse(user.is_author)

        Course.objects.create(title='Django basics', author=user)

        self.assertTrue(user.is_author)


class UsersAPITests(APITestCase):
    password = 'StrongPassword123!'

    def create_user(self, **extra_fields):
        data = {
            'email': 'user@example.com',
            'username': 'user',
            'password': self.password,
        }
        data.update(extra_fields)
        return get_user_model().objects.create_user(**data)

    def test_register_creates_user_and_hashes_password(self):
        response = self.client.post(
            reverse('auth_api:register'),
            {'email': 'new@example.com', 'username': 'new-user', 'password': self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

        user = get_user_model().objects.get(email='new@example.com')
        self.assertTrue(user.check_password(self.password))

    def test_register_rejects_duplicate_email(self):
        self.create_user()

        response = self.client.post(
            reverse('auth_api:register'),
            {'email': 'user@example.com', 'username': 'another', 'password': self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_access_and_refresh_tokens(self):
        self.create_user()

        response = self.client.post(
            reverse('auth_api:login'), {'email': 'user@example.com', 'password': self.password}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_rejects_wrong_password(self):
        self.create_user()

        response = self.client.post(
            reverse('auth_api:login'), {'email': 'user@example.com', 'password': 'wrong-password'}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse('users_api:me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user_profile(self):
        user = self.create_user()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('users_api:me'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@example.com')
        self.assertEqual(response.data['role'], 'user')
        self.assertFalse(response.data['is_author'])

    def test_me_patch_updates_own_profile(self):
        user = self.create_user()
        self.client.force_authenticate(user)

        response = self.client.patch(
            reverse('users_api:me'), {'bio': 'Backend developer', 'telegram_username': '@ualikhan'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.bio, 'Backend developer')
        self.assertEqual(user.telegram_username, 'ualikhan')

    def test_me_patch_cannot_change_email(self):
        user = self.create_user()
        self.client.force_authenticate(user)

        self.client.patch(reverse('users_api:me'), {'email': 'hacked@example.com'})

        user.refresh_from_db()
        self.assertEqual(user.email, 'user@example.com')

    def test_logout_blacklists_refresh_token(self):
        self.create_user()
        login_response = self.client.post(
            reverse('auth_api:login'), {'email': 'user@example.com', 'password': self.password}
        )
        access = login_response.data['access']
        refresh = login_response.data['refresh']

        response = self.client.post(
            reverse('auth_api:logout'),
            {'refresh': refresh},
            HTTP_AUTHORIZATION=f'Bearer {access}',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        refresh_response = self.client.post(reverse('auth_api:refresh'), {'refresh': refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

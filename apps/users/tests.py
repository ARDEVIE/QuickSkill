from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.courses.models import Course
from apps.users.forms import UserRegistrationForm


class UsersTests(TestCase):
    password = "StrongPassword123!"

    def create_user(self, **extra_fields):
        data = {
            "email": "user@example.com",
            "username": "user",
            "password": self.password,
        }
        data.update(extra_fields)
        return get_user_model().objects.create_user(**data)

    def test_registration_page_is_available(self):
        response = self.client.get(reverse("users:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_registration_rejects_different_passwords(self):
        form = UserRegistrationForm(
            data={
                "email": "new@example.com",
                "username": "new-user",
                "password1": self.password,
                "password2": "AnotherPassword123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "email": "new@example.com",
                "username": "new-user",
                "first_name": "New",
                "last_name": "User",
                "password1": self.password,
                "password2": self.password,
            },
        )

        user = get_user_model().objects.get(email="new@example.com")
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        self.assertRedirects(response, reverse("users:profile"))

    def test_profile_requires_login(self):
        response = self.client.get(reverse("users:profile"))

        login_url = reverse("users:login")
        profile_url = reverse("users:profile")
        self.assertRedirects(response, f"{login_url}?next={profile_url}")

    def test_profile_shows_authenticated_user(self):
        user = self.create_user()
        self.client.force_login(user)

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.email)
        self.assertContains(response, user.username)

    def test_user_can_update_own_profile(self):
        user = self.create_user()
        other = self.create_user(email="other@example.com", username="other")
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "first_name": "Updated",
                "last_name": "User",
                "telegram_username": "  @quickskill_user  ",
                "bio": "Backend developer",
            },
        )

        user.refresh_from_db()
        other.refresh_from_db()
        self.assertRedirects(response, reverse("users:profile"))
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.telegram_username, "quickskill_user")
        self.assertEqual(user.bio, "Backend developer")
        self.assertEqual(other.first_name, "")

    def test_logout_ends_session(self):
        user = self.create_user()
        self.client.force_login(user)

        response = self.client.post(reverse("users:logout"))

        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertRedirects(response, reverse("users:login"))

    def test_is_author_is_false_until_user_creates_a_course(self):
        user = self.create_user()
        self.assertFalse(user.is_author)

        Course.objects.create(title="Django basics", author=user)

        self.assertTrue(user.is_author)


class UsersAPITests(APITestCase):
    password = "StrongPassword123!"

    def create_user(self, **extra_fields):
        data = {
            "email": "user@example.com",
            "username": "user",
            "password": self.password,
        }
        data.update(extra_fields)
        return get_user_model().objects.create_user(**data)

    def test_register_creates_user_and_hashes_password(self):
        response = self.client.post(
            reverse("auth_api:register"),
            {"email": "new@example.com", "username": "new-user", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

        user = get_user_model().objects.get(email="new@example.com")
        self.assertTrue(user.check_password(self.password))

    def test_register_rejects_duplicate_email(self):
        self.create_user()

        response = self.client.post(
            reverse("auth_api:register"),
            {"email": "user@example.com", "username": "another", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_access_and_refresh_tokens(self):
        self.create_user()

        response = self.client.post(
            reverse("auth_api:login"), {"email": "user@example.com", "password": self.password}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_wrong_password(self):
        self.create_user()

        response = self.client.post(
            reverse("auth_api:login"), {"email": "user@example.com", "password": "wrong-password"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("users_api:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user_profile(self):
        user = self.create_user()
        self.client.force_authenticate(user)

        response = self.client.get(reverse("users_api:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@example.com")
        self.assertEqual(response.data["role"], "user")
        self.assertFalse(response.data["is_author"])

    def test_me_patch_updates_own_profile(self):
        user = self.create_user()
        self.client.force_authenticate(user)

        response = self.client.patch(
            reverse("users_api:me"), {"bio": "Backend developer", "telegram_username": "@ualikhan"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.bio, "Backend developer")
        self.assertEqual(user.telegram_username, "ualikhan")

    def test_me_patch_cannot_change_email(self):
        user = self.create_user()
        self.client.force_authenticate(user)

        self.client.patch(reverse("users_api:me"), {"email": "hacked@example.com"})

        user.refresh_from_db()
        self.assertEqual(user.email, "user@example.com")

    def test_logout_blacklists_refresh_token(self):
        self.create_user()
        login_response = self.client.post(
            reverse("auth_api:login"), {"email": "user@example.com", "password": self.password}
        )
        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        response = self.client.post(
            reverse("auth_api:logout"),
            {"refresh": refresh},
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        refresh_response = self.client.post(reverse("auth_api:refresh"), {"refresh": refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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

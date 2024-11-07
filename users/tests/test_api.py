from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.tests.factories import UserFactory


class UserApiTestCase(APITestCase):
    def test_requires_authentication(self):
        response = self.client.get(reverse("api:user"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_current_user(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("api:user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user.id)


class LoginApiTestCase(APITestCase):
    def test_authenticates_user_by_email_and_password_and_returns_token(self):
        user = UserFactory()
        user.set_password("random_password")
        user.save()
        response = self.client.post(
            reverse("api:rest_login"),
            {"email": user.email, "password": "random_password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["key"], user.auth_token.key)

    def test_returns_400_if_credentials_are_invalid(self):
        user = UserFactory()
        response = self.client.post(
            reverse("api:rest_login"),
            {"email": user.email, "password": "wrong_password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterApiTestCase(APITestCase):
    def test_registers_user_by_email_and_password_and_returns_token(self):
        response = self.client.post(
            reverse("api:rest_register"),
            {
                "email": "test@example.com",
                "password1": "testpassword",
                "password2": "testpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.auth_token.key, response.data["key"])

    def test_returns_400_if_email_is_already_taken(self):
        UserFactory(email="test@example.com")
        response = self.client.post(
            reverse("api:rest_register"),
            {
                "email": "test@example.com",
                "password1": "testpassword",
                "password2": "testpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_passwords_do_not_match(self):
        response = self.client.post(
            reverse("api:rest_register"),
            {
                "email": "test@example.com",
                "password1": "testpassword",
                "password2": "wrongpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_email_is_invalid(self):
        response = self.client.post(
            reverse("api:rest_register"),
            {
                "email": "invalid_email",
                "password1": "testpassword",
                "password2": "testpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_password_is_too_short(self):
        response = self.client.post(
            reverse("api:rest_register"),
            {"email": "test@example.com", "password1": "short", "password2": "short"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_email_is_missing(self):
        response = self.client.post(
            reverse("api:rest_register"),
            {"password1": "testpassword", "password2": "testpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_password_is_missing(self):
        response = self.client.post(
            reverse("api:rest_register"),
            {"email": "test@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

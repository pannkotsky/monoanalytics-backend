from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from data_imports.exceptions import ImportException
from users.tests.factories import UserFactory
from .factories import ProfileFactory


class ProfileApiTestCase(APITestCase):
    def test_list_profiles_requires_authentication(self):
        response = self.client.get(reverse("api:profile-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_profiles_returns_only_current_user_profiles(self):
        user = UserFactory()
        user_profiles = ProfileFactory.create_batch(2, user=user)
        ProfileFactory()

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("api:profile-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertCountEqual(
            [result["id"] for result in results],
            [profile.id for profile in user_profiles],
        )

    def test_retrieve_profile_requires_authentication(self):
        profile = ProfileFactory()
        response = self.client.get(reverse("api:profile-detail", args=[profile.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_profile_returns_current_user_profile(self):
        user = UserFactory()
        profile = ProfileFactory(user=user)
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("api:profile-detail", args=[profile.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], profile.id)

    def test_retrieve_someone_else_profile_returns_404(self):
        user = UserFactory()
        profile = ProfileFactory()
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("api:profile-detail", args=[profile.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_non_existent_profile_returns_404(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("api:profile-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("data_providers.provider_base.ProviderBase.import_profile")
    def test_import_profile_monobank_personal(self, import_profile_mock):
        user = UserFactory(first_name="", last_name="")
        profile = ProfileFactory(user=user, name="Мазепа Іван")
        import_profile_mock.return_value = profile

        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("api:profile-import-monobank-personal"),
            {"token": "test_token"},
            format="json",
        )
        import_profile_mock.assert_called_once_with({"token": "test_token"}, user.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], profile.id)

        # Check that user name was updated
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Іван")
        self.assertEqual(user.last_name, "Мазепа")

    def test_import_profile_requires_authentication(self):
        response = self.client.post(
            reverse("api:profile-import-monobank-personal"),
            {"token": "test_token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_import_profile_monobank_personal_provider_disabled(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        with self.settings(DATA_PROVIDERS={"MONOBANK_PERSONAL": {"ENABLED": False}}):
            response = self.client.post(
                reverse("api:profile-import-monobank-personal"),
                {"token": "test_token"},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_import_profile_monobank_personal_missing_token(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("api:profile-import-monobank-personal"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_profile_monobank_personal_blank_token(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("api:profile-import-monobank-personal"),
            {"token": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("data_providers.provider_base.ProviderBase.import_profile")
    def test_import_profile_monobank_personal_invalid_token(self, import_profile_mock):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        import_profile_mock.side_effect = ImportException(
            "Invalid token", status.HTTP_403_FORBIDDEN
        )
        response = self.client.post(
            reverse("api:profile-import-monobank-personal"),
            {"token": "test_token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("data_providers.provider_base.ProviderBase.import_profile")
    def test_import_profile_monobank_personal_too_many_requests(
        self, import_profile_mock
    ):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        import_profile_mock.side_effect = ImportException(
            "Too many requests", status.HTTP_429_TOO_MANY_REQUESTS
        )
        response = self.client.post(
            reverse("api:profile-import-monobank-personal"),
            {"token": "test_token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

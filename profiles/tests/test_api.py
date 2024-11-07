from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

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

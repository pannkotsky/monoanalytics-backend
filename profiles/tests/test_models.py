from django.db import DatabaseError
from django.test import TestCase

from .factories import ProfileFactory, UserFactory


class ProfileModelTestCase(TestCase):
    def test_name(self):
        profile = ProfileFactory(name="Test Name")
        self.assertEqual(profile.name, "Test Name")
        self.assertEqual(profile.raw_data, {})

    def test_unique_mono_id(self):
        user1 = UserFactory()
        profile1 = ProfileFactory(user=user1)
        with self.assertRaises(DatabaseError):
            ProfileFactory(user=user1, mono_id=profile1.mono_id)

    def test_unique_token(self):
        user1 = UserFactory()
        profile1 = ProfileFactory(user=user1)
        with self.assertRaises(DatabaseError):
            ProfileFactory(user=user1, token=profile1.token)

    def test_unique_name(self):
        user1 = UserFactory()
        profile1 = ProfileFactory(user=user1)
        with self.assertRaises(DatabaseError):
            ProfileFactory(user=user1, name=profile1.name)

    def test_allows_same_values_for_different_users(self):
        user1 = UserFactory()
        profile1 = ProfileFactory(user=user1)
        user2 = UserFactory()
        ProfileFactory(
            user=user2,
            mono_id=profile1.mono_id,
            token=profile1.token,
            name=profile1.name,
        )

from datetime import datetime

from django.test import TestCase

from data_providers.provider_base import ProviderBase
from profiles.models import Account, Jar, Profile
from statement.models import StatementItem
from users.tests.factories import UserFactory

test_profile_data = {
    "id_from_provider": "3MSaMMtczs",
    "name": "Мазепа Іван",
    "webhook_url": "https://example.com/some_random_data_for_security",
}
test_account_data = {
    "id_from_provider": "kKGVoZuHWzqVoZuH",
    "balance": 10000000,
    "currency_code": 980,
    "masked_pan": "537541******1234",
    "iban": "UA733220010000026201234567890",
}
test_jar_data = {
    "id_from_provider": "kKGVoZuHWzqVoZuH",
    "title": "На тепловізор",
    "description": "На тепловізор",
    "currency_code": 980,
    "balance": 1000000,
    "goal": 1000000,
}


class TestingProvider(ProviderBase):
    name = "testing_provider"

    def profile_adapter(self, data: dict):
        return Profile(**data, raw_data=data)

    def account_adapter(self, data: dict):
        return Account(**data, raw_data=data)

    def jar_adapter(self, data: dict):
        return Jar(**data, raw_data=data)

    def statement_item_adapter(self, data: dict):
        return StatementItem(**data, raw_data=data)

    def fetch_profile_data(self, auth_data: dict):
        return {
            "profile": test_profile_data,
            "accounts": [test_account_data],
            "jars": [test_jar_data],
        }

    def fetch_statement_data(
        self, auth_data: dict, account: Account, from_date: datetime, to_date: datetime
    ):
        return []


class TestProviderBase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.provider = TestingProvider()

    def test_import_profile(self):
        profile = self.provider.import_profile(test_profile_data, user_id=self.user.id)
        self.assertEqual(
            profile.id_from_provider, test_profile_data["id_from_provider"]
        )
        self.assertEqual(profile.provider_name, self.provider.name)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.name, test_profile_data["name"])
        self.assertEqual(profile.webhook_url, test_profile_data["webhook_url"])
        self.assertEqual(profile.raw_data, test_profile_data)

        self.assertEqual(profile.accounts.count(), 1)
        account = profile.accounts.first()
        self.assertEqual(
            account.id_from_provider, test_account_data["id_from_provider"]
        )
        self.assertEqual(account.balance, test_account_data["balance"])
        self.assertEqual(account.currency_code, test_account_data["currency_code"])
        self.assertEqual(account.masked_pan, test_account_data["masked_pan"])
        self.assertEqual(account.iban, test_account_data["iban"])

        self.assertEqual(profile.jars.count(), 1)
        jar = profile.jars.first()
        self.assertEqual(jar.id_from_provider, test_jar_data["id_from_provider"])
        self.assertEqual(jar.title, test_jar_data["title"])
        self.assertEqual(jar.description, test_jar_data["description"])
        self.assertEqual(jar.currency_code, test_jar_data["currency_code"])
        self.assertEqual(jar.balance, test_jar_data["balance"])
        self.assertEqual(jar.goal, test_jar_data["goal"])

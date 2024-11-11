from unittest import TestCase
from unittest.mock import patch

import monobank

from data_imports.exceptions import ImportException
from data_providers.monobank.providers import MonobankPersonalProvider, PersonalAuthData
from data_providers.monobank.types import (
    MonobankAccountData,
    MonobankJarData,
    MonobankProfileData,
    MonobankRawProfileData,
)

test_profile_data: MonobankProfileData = {
    "clientId": "3MSaMMtczs",
    "name": "Мазепа Іван",
    "webHookUrl": "https://example.com/some_random_data_for_security",
    "permissions": "psfj",
}
test_account_data: MonobankAccountData = {
    "id": "kKGVoZuHWzqVoZuH",
    "sendId": "uHWzqVoZuH",
    "balance": 10000000,
    "creditLimit": 10000000,
    "type": "black",
    "currencyCode": 980,
    "cashbackType": "UAH",
    "maskedPan": ["537541******1234"],
    "iban": "UA733220010000026201234567890",
}
test_jar_data: MonobankJarData = {
    "id": "kKGVoZuHWzqVoZuH",
    "sendId": "uHWzqVoZuH",
    "title": "На тепловізор",
    "description": "На тепловізор",
    "currencyCode": 980,
    "balance": 1000000,
    "goal": 1000000,
}
test_client_info: MonobankRawProfileData = {
    **test_profile_data,
    "accounts": [test_account_data],
    "jars": [test_jar_data],
}


class MockMonobankResponse:
    status_code = 403


class TestMonobankPersonalProvider(TestCase):
    def test_profile_adapter(self):
        provider = MonobankPersonalProvider()
        profile = provider.profile_adapter(test_client_info)
        self.assertEqual(profile.id_from_provider, test_profile_data["clientId"])
        self.assertEqual(profile.name, test_profile_data["name"])
        self.assertEqual(profile.webhook_url, test_profile_data["webHookUrl"])
        self.assertEqual(profile.raw_data, test_client_info)

    def test_account_adapter(self):
        provider = MonobankPersonalProvider()
        account = provider.account_adapter(test_account_data)
        self.assertEqual(account.id_from_provider, test_account_data["id"])
        self.assertEqual(account.balance, test_account_data["balance"])
        self.assertEqual(account.credit_limit, test_account_data["creditLimit"])
        self.assertEqual(account.type, test_account_data["type"])
        self.assertEqual(account.currency_code, test_account_data["currencyCode"])
        self.assertEqual(account.masked_pan, test_account_data["maskedPan"][0])
        self.assertEqual(account.iban, test_account_data["iban"])
        self.assertEqual(account.raw_data, test_account_data)

    def test_jar_adapter(self):
        provider = MonobankPersonalProvider()
        jar = provider.jar_adapter(test_jar_data)
        self.assertEqual(jar.id_from_provider, test_jar_data["id"])
        self.assertEqual(jar.title, test_jar_data["title"])
        self.assertEqual(jar.description, test_jar_data["description"])
        self.assertEqual(jar.currency_code, test_jar_data["currencyCode"])
        self.assertEqual(jar.balance, test_jar_data["balance"])
        self.assertEqual(jar.goal, test_jar_data["goal"])
        self.assertEqual(jar.raw_data, test_jar_data)

    @patch("monobank.client.Client.get_client_info")
    def test_fetch_profile_data_success(self, mock_get_client_info):
        mock_get_client_info.return_value = test_client_info
        provider = MonobankPersonalProvider()
        auth_data: PersonalAuthData = {"token": "test_token"}
        result = provider.fetch_profile_data(auth_data)
        self.assertEqual(result["profile"], test_profile_data)
        self.assertEqual(result["accounts"], [test_account_data])
        self.assertEqual(result["jars"], [test_jar_data])

    @patch("monobank.client.Client.get_client_info")
    def test_fetch_profile_data_error(self, mock_get_client_info):
        mock_get_client_info.side_effect = monobank.Error(
            "invalid token", MockMonobankResponse()
        )
        provider = MonobankPersonalProvider()
        auth_data: PersonalAuthData = {"token": "test_token"}
        with self.assertRaises(ImportException):
            provider.fetch_profile_data(auth_data)

import time
from datetime import datetime
from typing import Iterable, TypedDict

from django.utils import timezone

import monobank

from data_imports.exceptions import ImportException
from data_imports.models.provider import ProfileDataWithAccounts, Provider
from profiles.models import Account, Jar, Profile
from statement.models import StatementItem
from .types import (
    MonobankAccountData,
    MonobankJarData,
    MonobankProfileData,
    MonobankRawProfileData,
    MonobankStatementItemData,
)


class PersonalAuthData(TypedDict):
    token: str


class CorporateAuthData(TypedDict):
    request_id: str


class MonobankProviderBaseMixin:
    @property
    def rate_limit(self) -> int:
        return 60

    def profile_adapter(self, data: MonobankProfileData) -> Profile:
        return Profile(
            id_from_provider=data["clientId"],
            name=data["name"],
            webhook_url=data["webHookUrl"],
            raw_data=data,
        )

    def account_adapter(self, data: MonobankAccountData) -> Account:
        return Account(
            id_from_provider=data["id"],
            balance=data["balance"],
            credit_limit=data["creditLimit"],
            type=data["type"],
            currency_code=data["currencyCode"],
            masked_pan=data["maskedPan"][0] if data["maskedPan"] else "",
            iban=data["iban"],
            raw_data=data,
        )

    def jar_adapter(self, data: MonobankJarData) -> Jar:
        return Jar(
            id_from_provider=data["id"],
            title=data["title"],
            description=data["description"],
            currency_code=data["currencyCode"],
            balance=data["balance"],
            goal=data["goal"],
            raw_data=data,
        )

    def statement_item_adapter(self, data: MonobankStatementItemData) -> StatementItem:
        return StatementItem(
            id_from_provider=data["id"],
            time=timezone.make_aware(datetime.fromtimestamp(data["time"])),
            description=data["description"],
            merchant_category_id=data["mcc"],
            hold=data["hold"],
            amount_in_account_currency=data["amount"],
            amount_in_operation_currency=data["operationAmount"],
            currency_code=data["currencyCode"],
            commission_rate=data["commissionRate"],
            cashback_amount=data["cashbackAmount"],
            balance=data["balance"],
            counter_name=data.get("counterName", ""),
            raw_data=data,
        )

    def get_client(self, auth_data: dict):
        raise NotImplementedError

    def fetch_profile_data(
        self, auth_data: dict
    ) -> ProfileDataWithAccounts[
        MonobankProfileData, MonobankAccountData, MonobankJarData
    ]:
        client = self.get_client(auth_data)
        try:
            client_info: MonobankRawProfileData = client.get_client_info()
        except monobank.Error as e:
            raise ImportException(e.args[0], e.response.status_code) from e
        return {
            "profile": {
                "clientId": client_info["clientId"],
                "name": client_info["name"],
                "webHookUrl": client_info["webHookUrl"],
                "permissions": client_info["permissions"],
            },
            "accounts": client_info["accounts"],
            "jars": client_info["jars"],
        }

    def fetch_statement_items_data_chunk(
        self, client, account_id: str, start_date: datetime, finish_date: datetime
    ) -> Iterable[MonobankStatementItemData]:
        statement_items_data: list[MonobankStatementItemData] = client.get_statements(
            account_id, start_date, finish_date
        )
        yield from statement_items_data

        # Monobank API returns 500 operations max in reverse chronological order
        # If 500 operations are returned, the next chunk should be fetched for time until the time
        # of the last operation in the current chunk
        # https://api.monobank.ua/docs/index.html#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get
        if len(statement_items_data) == 500:
            finish_date = timezone.make_aware(
                datetime.fromtimestamp(statement_items_data[-1]["time"])
            )
            yield from self.fetch_statement_items_data_chunk(
                client, account_id, start_date, finish_date
            )

    def fetch_statement_items_data(
        self,
        auth_data: dict,
        account: Account,
        from_date: datetime,
        to_date: datetime,
    ) -> Iterable[MonobankStatementItemData]:
        client = self.get_client(auth_data)

        finish_date = to_date

        while True:
            start_date = max(finish_date - timezone.timedelta(days=30), from_date)
            yield from self.fetch_statement_items_data_chunk(
                client, account.id_from_provider, start_date, finish_date
            )
            finish_date = start_date
            if finish_date <= from_date:
                break
            time.sleep(self.rate_limit)


class MonobankPersonalProvider(MonobankProviderBaseMixin, Provider):
    class Meta:
        proxy = True

    provider_name = "monobank_personal"

    def get_client(self, auth_data: PersonalAuthData):
        return monobank.Client(auth_data["token"])


class MonobankCorporateProvider(MonobankProviderBaseMixin, Provider):
    class Meta:
        proxy = True

    provider_name = "monobank_corporate"

    def get_client(self, auth_data: CorporateAuthData):
        return monobank.CorporateClient(auth_data["request_id"], self.private_key)

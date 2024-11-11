import abc
from datetime import datetime
from typing import Iterable, TypedDict

from django.db import transaction
from django.utils import timezone

from data_imports.models.statement_import import StatementImport
from profiles.models import Account, Jar, Profile
from statement.models import StatementItem


class ProfileDataWithAccounts[ProfileData, AccountData, JarData](TypedDict):
    profile: ProfileData
    accounts: list[AccountData]
    jars: list[JarData]


class ProviderBase[AuthData, ProfileData, AccountData, JarData, StatementItemData](
    abc.ABC
):
    name = ""

    def __init__(self):
        assert self.name, "Provider name is not set"

    def profile_adapter(self, data: ProfileData) -> Profile:
        """
        Adapts data from provider to Profile model instance (unsaved)
        """
        raise NotImplementedError

    def account_adapter(self, data: AccountData) -> Account:
        """
        Adapts data from provider to Account model instance (unsaved)
        """
        raise NotImplementedError

    def jar_adapter(self, data: JarData) -> Jar:
        """
        Adapts data from provider to Jar model instance (unsaved)
        """
        raise NotImplementedError

    def statement_item_adapter(self, data: StatementItemData) -> StatementItem:
        """
        Adapts data from provider to StatementItem model instance (unsaved)
        """
        raise NotImplementedError

    def fetch_profile_data(
        self, auth_data: AuthData
    ) -> ProfileDataWithAccounts[ProfileData, AccountData, JarData]:
        """
        Fetches profile data from provider
        """
        raise NotImplementedError

    @transaction.atomic
    def import_profile(self, auth_data: AuthData, user_id: int) -> Profile:
        """
        Fetches profile data from provider and imports it into the database
        """
        data = self.fetch_profile_data(auth_data)
        profile_data = data["profile"]
        accounts_data = data["accounts"]
        jars_data = data["jars"]

        profile = self.profile_adapter(profile_data)
        existing_profile = Profile.objects.filter(
            provider_name=self.name,
            id_from_provider=profile.id_from_provider,
            user_id=user_id,
        ).first()
        if existing_profile:
            for field in Profile._meta.concrete_fields:
                if field.name not in ("provider_name", "id_from_provider", "user"):
                    setattr(existing_profile, field.name, getattr(profile, field.name))
            existing_profile.save()
        else:
            profile.provider_name = self.name
            profile.user_id = user_id
            profile.save()

        for account_data in accounts_data:
            account = self.account_adapter(account_data)

            existing_account = Account.objects.filter(
                id_from_provider=account.id_from_provider, profile=profile
            ).first()
            if existing_account:
                for field in Account._meta.concrete_fields:
                    if field.name not in ("id_from_provider", "profile"):
                        setattr(
                            existing_account, field.name, getattr(account, field.name)
                        )
                existing_account.save()
            else:
                account.profile = profile
                account.save()

        for jar_data in jars_data:
            jar = self.jar_adapter(jar_data)

            existing_jar = Jar.objects.filter(
                id_from_provider=jar.id_from_provider, profile=profile
            ).first()
            if existing_jar:
                for field in Jar._meta.concrete_fields:
                    if field.name not in ("id_from_provider", "profile"):
                        setattr(existing_jar, field.name, getattr(jar, field.name))
                existing_jar.save()
            else:
                jar.profile = profile
                jar.save()

        return profile

    def fetch_statement_items_data(
        self,
        auth_data: AuthData,
        account: Account,
        from_date: datetime,
        to_date: datetime,
    ) -> Iterable[StatementItemData]:
        """
        Fetches statement items data from provider
        """
        raise NotImplementedError

    def import_statement_items(
        self,
        auth_data: AuthData,
        account: Account,
        from_date: datetime,
        to_date: datetime | None = None,
    ):
        """
        Fetches statement items from provider and imports them into the database
        """

        # TODO: move it to Celery task to return import id immediately for tracking
        statement_import = StatementImport.objects.create(account=account)

        to_date = to_date or timezone.localtime()

        try:
            statement_items_data = self.fetch_statement_items_data(
                auth_data, account, from_date, to_date
            )
            for statement_item_data in statement_items_data:
                statement_item = self.statement_item_adapter(statement_item_data)
                if StatementItem.objects.filter(
                    id_from_provider=statement_item.id_from_provider,
                    account=account,
                ).exists():
                    continue
                statement_item.account = account
                statement_item.save()
                statement_import.imported_items_count += 1
                statement_import.save()
        except Exception as e:
            statement_import.status = StatementImport.Status.FAILED
            statement_import.error = str(e)
            raise
        else:
            statement_import.status = StatementImport.Status.FINISHED
        finally:
            statement_import.finished_at = timezone.localtime()
            statement_import.save()

import factory

from data_imports.models import (
    MonobankCorporateProvider,
    MonobankPersonalProvider,
    Provider,
)


class ProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Provider
        abstract = True
        django_get_or_create = ("name",)

    name = factory.Faker("word")


class MonobankPersonalProviderFactory(ProviderFactory):
    class Meta:
        model = MonobankPersonalProvider

    name = MonobankPersonalProvider.provider_name


class MonobankCorporateProviderFactory(ProviderFactory):
    class Meta:
        model = MonobankCorporateProvider

    name = MonobankCorporateProvider.provider_name

import factory

from profiles.models import Profile
from users.tests.factories import UserFactory


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    provider_name = "monobank_personal"
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Profile {n}")
    id_from_provider = factory.Faker("uuid4")
    raw_data = {}

import factory

from profiles.models import Profile
from users.tests.factories import UserFactory


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Profile {n}")
    mono_id = factory.Faker("uuid4")
    token = factory.Faker("uuid4")
    raw_data = {}

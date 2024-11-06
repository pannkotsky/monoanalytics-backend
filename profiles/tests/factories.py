from django.contrib.auth.models import User

import factory

from profiles.models import Profile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("email")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    mono_id = factory.Faker("uuid4")
    token = factory.Faker("uuid4")
    raw_data = {}

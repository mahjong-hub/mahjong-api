import uuid

import factory

from user.models import Client


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    install_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    label = factory.Faker('word')

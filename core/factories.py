import factory

from core.models import Tile, TileSet


class TileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tile
        django_get_or_create = ['code']

    code = factory.Sequence(lambda n: f'{(n % 9) + 1}B')
    suit = 'B'
    rank = factory.LazyAttribute(
        lambda o: int(o.code[0]) if o.code[0].isdigit() else None,
    )
    label = factory.LazyAttribute(
        lambda o: {
            'en': o.code,
            'zh-hk': o.code,
            'zh-cn': o.code,
        },
    )


class TileSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TileSet
        django_get_or_create = ['code']

    code = factory.Sequence(lambda n: f'FAKE_CODE_{n}')
    description = factory.Faker('sentence')

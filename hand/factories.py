from decimal import Decimal

import factory

from asset.constants import AssetRole
from asset.factories import AssetFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus, HandSource
from hand.models import DetectionTile, Hand, HandDetection
from user.factories import ClientFactory


class HandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hand

    client = factory.SubFactory(ClientFactory)
    source = HandSource.CAMERA.value


class HandDetectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HandDetection
        exclude = ['_asset']

    hand = factory.SubFactory(HandFactory)

    # Internal: create an active asset to attach via AssetRef
    _asset = factory.LazyAttribute(
        lambda o: AssetFactory(
            upload_session=UploadSessionFactory(client=o.hand.client),
            is_active=True,
        ),
    )

    asset_ref = factory.LazyAttribute(
        lambda o: AssetRef.attach(
            asset=o._asset,
            owner=o.hand,
            role=AssetRole.HAND_PHOTO.value,
        ),
    )

    status = DetectionStatus.PENDING.value
    model_name = 'tile_detector'
    model_version = 'v0'


class DetectionTileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DetectionTile

    detection = factory.SubFactory(HandDetectionFactory)
    tile_code = '1B'
    x1 = 10
    y1 = 20
    x2 = 110
    y2 = 120
    confidence = Decimal('0.9500')

import uuid

import factory

from asset.constants import StorageProvider, UploadStatus
from asset.models import Asset, UploadSession
from user.factories import ClientFactory


class UploadSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UploadSession

    client = factory.SubFactory(ClientFactory)
    status = UploadStatus.CREATED.value
    purpose = 'hand_photo'


class AssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Asset

    upload_session = factory.SubFactory(UploadSessionFactory)
    is_active = False
    storage_provider = StorageProvider.R2.value
    storage_key = factory.LazyAttribute(
        lambda o: f'uploads/{o.upload_session.client.install_id}/{uuid.uuid4()}.jpg',
    )
    mime_type = 'image/jpeg'
    byte_size = 0

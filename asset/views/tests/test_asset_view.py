from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from asset.constants import UploadStatus
from asset.factories import AssetFactory, ClientFactory, UploadSessionFactory
from asset.services.s3 import S3ObjectMetadata


class TestAssetViewSetRetrieve(APITestCase):
    def test_success(self):
        session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
        asset = AssetFactory(upload_session=session, is_active=True)

        response = self.client.get(
            f'/asset/{asset.id}/',
            HTTP_X_INSTALL_ID=session.client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(asset.id))
        self.assertIn('upload_session_id', response.data)
        self.assertIn('storage_key', response.data)
        self.assertIn('is_active', response.data)

    def test_not_found(self):
        client = ClientFactory()

        response = self.client.get(
            '/asset/00000000-0000-0000-0000-000000000000/',
            HTTP_X_INSTALL_ID=client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ownership_validation(self):
        session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
        asset = AssetFactory(upload_session=session)
        other_client = ClientFactory()

        response = self.client.get(
            f'/asset/{asset.id}/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_install_id_header(self):
        session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
        asset = AssetFactory(upload_session=session)

        response = self.client.get(f'/asset/{asset.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestAssetViewSetComplete(APITestCase):
    @patch('asset.services.uploads.head_object')
    def test_success(self, mock_head):
        mock_head.return_value = S3ObjectMetadata(
            content_type='image/jpeg',
            content_length=12345,
            etag='"abc123"',
        )
        session = UploadSessionFactory(status=UploadStatus.PRESIGNED.value)
        asset = AssetFactory(upload_session=session)

        response = self.client.post(
            f'/asset/{asset.id}/upload/complete/',
            HTTP_X_INSTALL_ID=session.client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('upload_session_id', response.data)
        self.assertIn('id', response.data)
        self.assertIn('is_active', response.data)
        self.assertIn('byte_size', response.data)
        self.assertIn('checksum', response.data)
        self.assertTrue(response.data['is_active'])
        self.assertEqual(response.data['byte_size'], 12345)

    @patch('asset.services.uploads.head_object')
    def test_file_not_uploaded(self, mock_head):
        mock_head.return_value = None
        session = UploadSessionFactory(status=UploadStatus.PRESIGNED.value)
        asset = AssetFactory(upload_session=session)

        response = self.client.post(
            f'/asset/{asset.id}/upload/complete/',
            HTTP_X_INSTALL_ID=session.client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'upload_not_complete')

    def test_missing_install_id_header(self):
        session = UploadSessionFactory(status=UploadStatus.PRESIGNED.value)
        asset = AssetFactory(upload_session=session)

        response = self.client.post(f'/asset/{asset.id}/upload/complete/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('asset.services.uploads.head_object')
    def test_ownership_validation(self, mock_head):
        session = UploadSessionFactory(status=UploadStatus.PRESIGNED.value)
        asset = AssetFactory(upload_session=session)
        other_client = ClientFactory()

        response = self.client.post(
            f'/asset/{asset.id}/upload/complete/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

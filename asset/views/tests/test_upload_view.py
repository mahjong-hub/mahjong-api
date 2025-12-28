from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from asset.factories import ClientFactory


class TestUploadViewSetPresign(APITestCase):
    @patch('asset.services.uploads.generate_presigned_put_url')
    def test_success(self, mock_presign):
        mock_presign.return_value = 'https://s3.example.com/presigned'
        client = ClientFactory()

        response = self.client.post(
            '/asset/upload/presign/',
            {'content_type': 'image/jpeg', 'purpose': 'hand_photo'},
            HTTP_X_INSTALL_ID=client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('upload_session_id', response.data)
        self.assertIn('id', response.data)
        self.assertIn('presigned_url', response.data)
        self.assertIn('storage_key', response.data)

    def test_invalid_content_type(self):
        client = ClientFactory()

        response = self.client.post(
            '/asset/upload/presign/',
            {'content_type': 'application/pdf'},
            HTTP_X_INSTALL_ID=client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_install_id_header(self):
        response = self.client.post(
            '/asset/upload/presign/',
            {'content_type': 'image/jpeg'},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_content_type(self):
        client = ClientFactory()

        response = self.client.post(
            '/asset/upload/presign/',
            {},
            HTTP_X_INSTALL_ID=client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

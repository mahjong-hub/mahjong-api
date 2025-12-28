from django.test import TestCase

from asset.serializers.uploads_serializer import PresignRequestSerializer


class TestPresignRequestSerializer(TestCase):
    def test_valid_data(self):
        data = {
            'content_type': 'image/jpeg',
            'purpose': 'hand_photo',
        }
        serializer = PresignRequestSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['content_type'],
            'image/jpeg',
        )

    def test_valid_without_purpose(self):
        data = {
            'content_type': 'image/png',
        }
        serializer = PresignRequestSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_invalid_missing_content_type(self):
        data = {}
        serializer = PresignRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('content_type', serializer.errors)

    def test_invalid_content_type_not_in_choices(self):
        data = {
            'content_type': 'application/pdf',
        }
        serializer = PresignRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('content_type', serializer.errors)

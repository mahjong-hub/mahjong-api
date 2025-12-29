from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from user.models import Client
from user.serializers import ClientSerializer


class TestClientSerializerValidation(TestCase):
    def test_valid_with_install_id_only(self):
        serializer = ClientSerializer(data={'install_id': 'test-123'})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['install_id'], 'test-123')
        self.assertEqual(serializer.validated_data['label'], '')

    def test_valid_with_install_id_and_label(self):
        serializer = ClientSerializer(
            data={'install_id': 'test-456', 'label': 'My Device'},
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['label'], 'My Device')

    def test_invalid_without_install_id(self):
        serializer = ClientSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('install_id', serializer.errors)

    def test_invalid_with_empty_install_id(self):
        serializer = ClientSerializer(data={'install_id': ''})

        self.assertFalse(serializer.is_valid())
        self.assertIn('install_id', serializer.errors)

    def test_allows_blank_label(self):
        serializer = ClientSerializer(
            data={'install_id': 'test-789', 'label': ''},
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['label'], '')

    def test_install_id_max_length(self):
        serializer = ClientSerializer(data={'install_id': 'x' * 65})

        self.assertFalse(serializer.is_valid())
        self.assertIn('install_id', serializer.errors)


class TestClientSerializerCreate(TestCase):
    def test_creates_new_client(self):
        serializer = ClientSerializer(data={'install_id': 'new-install-123'})
        serializer.is_valid(raise_exception=True)

        client, created = serializer.save()

        self.assertTrue(created)
        self.assertEqual(client.install_id, 'new-install-123')
        self.assertEqual(client.label, '')
        self.assertIsNotNone(client.created_at)
        self.assertIsNotNone(client.last_seen_at)

    def test_creates_new_client_with_label(self):
        serializer = ClientSerializer(
            data={'install_id': 'new-install-456', 'label': 'My iPhone'},
        )
        serializer.is_valid(raise_exception=True)

        client, created = serializer.save()

        self.assertTrue(created)
        self.assertEqual(client.label, 'My iPhone')

    def test_returns_existing_client(self):
        existing = Client.objects.create(install_id='existing-123')

        serializer = ClientSerializer(data={'install_id': 'existing-123'})
        serializer.is_valid(raise_exception=True)
        client, created = serializer.save()

        self.assertFalse(created)
        self.assertEqual(client.install_id, existing.install_id)
        self.assertEqual(Client.objects.count(), 1)

    def test_updates_last_seen_at_for_existing_client(self):
        old_time = timezone.now() - timedelta(hours=1)
        existing = Client.objects.create(install_id='existing-456')
        existing.last_seen_at = old_time
        existing.save()

        serializer = ClientSerializer(data={'install_id': 'existing-456'})
        serializer.is_valid(raise_exception=True)
        client, created = serializer.save()

        self.assertFalse(created)
        self.assertGreater(client.last_seen_at, old_time)

    def test_updates_label_for_existing_client(self):
        Client.objects.create(install_id='existing-789', label='Old Label')

        serializer = ClientSerializer(
            data={'install_id': 'existing-789', 'label': 'New Label'},
        )
        serializer.is_valid(raise_exception=True)
        client, created = serializer.save()

        self.assertFalse(created)
        self.assertEqual(client.label, 'New Label')

    def test_does_not_update_label_if_empty(self):
        Client.objects.create(install_id='existing-abc', label='Keep This')

        serializer = ClientSerializer(
            data={'install_id': 'existing-abc', 'label': ''},
        )
        serializer.is_valid(raise_exception=True)
        client, created = serializer.save()

        self.assertFalse(created)
        self.assertEqual(client.label, 'Keep This')


class TestClientSerializerRead(TestCase):
    def test_serializes_client_data(self):
        now = timezone.now()
        client = Client.objects.create(
            install_id='client-123',
            label='Test Device',
        )
        client.created_at = now
        client.last_seen_at = now
        client.save()

        serializer = ClientSerializer(instance=client)

        self.assertEqual(serializer.data['install_id'], 'client-123')
        self.assertEqual(serializer.data['label'], 'Test Device')
        self.assertIn('created_at', serializer.data)
        self.assertIn('last_seen_at', serializer.data)

from django.test import TestCase

from user.exceptions import ClientNotFound
from user.models import Client
from user.services import delete_client, get_client


class TestGetClient(TestCase):
    def test_returns_client(self):
        Client.objects.create(install_id='get-test-123')

        client = get_client(install_id='get-test-123')

        self.assertEqual(client.install_id, 'get-test-123')

    def test_raises_for_nonexistent_client(self):
        with self.assertRaises(ClientNotFound):
            get_client(install_id='nonexistent')


class TestDeleteClient(TestCase):
    def test_deletes_client(self):
        Client.objects.create(install_id='delete-test-123')

        delete_client(install_id='delete-test-123')

        self.assertEqual(Client.objects.count(), 0)

    def test_raises_for_nonexistent_client(self):
        with self.assertRaises(ClientNotFound):
            delete_client(install_id='nonexistent')

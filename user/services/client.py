from core.exceptions import catch_and_reraise
from user.exceptions import ClientNotFound
from user.models import Client


def get_client(*, install_id: str) -> Client:
    """
    Get a client by install_id.

    Raises Client.DoesNotExist if not found.
    """
    with catch_and_reraise(
        Client.DoesNotExist,
        ClientNotFound,
        f"Client with install_id '{install_id}' not found",
    ):
        return Client.objects.get(install_id=install_id)


def delete_client(*, install_id: str) -> None:
    """
    Delete a client by install_id.

    Raises Client.DoesNotExist if not found.
    """
    with catch_and_reraise(
        Client.DoesNotExist,
        ClientNotFound,
        f"Client with install_id '{install_id}' not found",
    ):
        client = Client.objects.get(install_id=install_id)
        client.delete()

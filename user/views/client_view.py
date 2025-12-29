from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from user.exceptions import MissingInstallIdHeader
from user.models import Client
from user.serializers import ClientSerializer
from user.services import delete_client, get_client


INSTALL_ID_HEADER = 'HTTP_X_INSTALL_ID'


def get_install_id(request: Request) -> str:
    """Extract install_id header."""
    install_id = request.META.get(INSTALL_ID_HEADER)
    if not install_id:
        raise MissingInstallIdHeader()

    return install_id


class ClientViewSet(viewsets.GenericViewSet):
    """
    ViewSet for client identity management.

    Endpoints:
        PUT /user/client/
        GET /user/client/me/
        DELETE /user/client/me/
    """

    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    def update(self, request: Request) -> Response:
        """
        Get or create a client by install_id.
        Updates last_seen_at if client exists.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client, created = serializer.save()

        response_serializer = self.get_serializer(instance=client)
        response_status = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
        return Response(response_serializer.data, status=response_status)

    @action(detail=False, methods=['get', 'delete'], url_path='me')
    def me(self, request: Request) -> Response:
        """
        Get or delete the current client identified by X-Install-Id header.
        """
        install_id = get_install_id(request)

        if request.method == 'GET':
            client = get_client(install_id=install_id)
            response_serializer = self.get_serializer(instance=client)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        elif request.method == 'DELETE':
            delete_client(install_id=install_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

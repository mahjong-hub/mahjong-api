from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from asset.models import Asset
from asset.serializers.asset_serializer import AssetSerializer
from asset.services.uploads import complete_upload
from asset.views.upload_view import get_install_id


class AssetViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for asset-level operations.

    Endpoints:
        GET /asset/{id}/
        POST /asset/{id}/upload/complete/
    """

    serializer_class = AssetSerializer

    def get_queryset(self):
        """Filter assets by client ownership."""
        install_id = get_install_id(self.request)
        return Asset.objects.filter(
            upload_session__client__install_id=install_id,
        ).select_related('upload_session')

    @action(detail=True, methods=['post'], url_path='upload/complete')
    def complete(self, request: Request, pk: str) -> Response:
        """Complete an upload by verifying file exists and updating metadata."""
        install_id = get_install_id(request)

        asset = complete_upload(
            asset_id=pk,
            install_id=install_id,
        )

        response_serializer = self.get_serializer(instance=asset)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

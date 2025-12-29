from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from asset.models import Asset
from asset.serializers.asset_serializer import AssetSerializer
from asset.serializers.uploads_serializer import PresignRequestSerializer
from asset.services.uploads import complete_upload, create_presigned_upload
from user.views import get_install_id


class AssetViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for asset-level operations.

    Endpoints:
        POST /asset/presigned-url/
        GET /asset/{id}/
        POST /asset/{id}/complete/
    """

    serializer_class = AssetSerializer

    def get_queryset(self):
        """Filter assets by client ownership."""
        install_id = get_install_id(self.request)
        return Asset.objects.filter(
            upload_session__client__install_id=install_id,
        ).select_related('upload_session')

    @action(detail=False, methods=['post'], url_path='presigned-url')
    def presigned_url(self, request: Request) -> Response:
        """Generate a presigned URL for uploading an asset."""
        install_id = get_install_id(request)

        serializer = PresignRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = create_presigned_upload(
            install_id=install_id,
            content_type=serializer.validated_data['content_type'],
            purpose=serializer.validated_data.get('purpose'),
        )

        response_serializer = self.get_serializer(instance=result['asset'])
        response_data = response_serializer.data
        response_data['presigned_url'] = result['presigned_url']

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request: Request, pk: str) -> Response:
        """Complete an upload by verifying file exists and updating metadata."""
        install_id = get_install_id(request)

        asset = complete_upload(
            asset_id=pk,
            install_id=install_id,
        )

        response_serializer = self.get_serializer(instance=asset)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

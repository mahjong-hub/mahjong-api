from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from asset.models import Asset
from asset.serializers.asset_serializer import AssetSerializer
from asset.serializers.uploads_serializer import PresignRequestSerializer
from asset.services.uploads import create_presigned_upload

INSTALL_ID_HEADER = 'X-Install-Id'


def get_install_id(request: Request) -> str:
    """Extract install_id from X-Install-Id header."""
    install_id = request.headers.get(INSTALL_ID_HEADER)
    if not install_id:
        raise NotAuthenticated(
            detail=f'Missing required header: {INSTALL_ID_HEADER}',
        )
    return install_id


class UploadViewSet(viewsets.GenericViewSet):
    """
    ViewSet for handling presigned upload flow.

    Endpoints:
        POST /asset/upload/presign/
    """

    serializer_class = AssetSerializer
    queryset = Asset.objects.all()

    def get_queryset(self):
        """Filter assets by client ownership."""
        install_id = get_install_id(self.request)
        return Asset.objects.filter(
            upload_session__client__install_id=install_id,
        ).select_related('upload_session')

    @action(detail=False, methods=['post'], url_path='presign')
    def presign(self, request: Request) -> Response:
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

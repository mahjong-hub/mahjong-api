from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from asset.models import Asset
from user.views import get_install_id
from hand.constants import HandSource
from hand.models import HandDetection
from hand.serializers.hand_detection_serializer import HandDetectionSerializer
from hand.services.hand_detection import (
    create_detection,
    enqueue_detection_task,
    find_existing_detection,
)
from user.models import Client


class HandDetectionViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for hand detection operations.

    Endpoints:
        POST /hand/detection/
        GET /hand/detection/{id}/
    """

    serializer_class = HandDetectionSerializer

    def get_queryset(self):
        """Filter detections by client ownership."""
        install_id = get_install_id(self.request)
        return (
            HandDetection.objects.filter(hand__client__install_id=install_id)
            .select_related('hand', 'asset_ref')
            .prefetch_related('tiles')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['install_id'] = get_install_id(self.request)
        return context

    def create(self, request, *args, **kwargs):
        """Trigger detection on an uploaded asset."""
        install_id = get_install_id(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asset_id = serializer.validated_data['asset_id']
        source = serializer.validated_data.get(
            'source',
            HandSource.CAMERA.value,
        )
        asset = Asset.objects.get(id=asset_id)

        detection = find_existing_detection(asset)
        created = False

        if not detection:
            # Create new detection and enqueue task
            client = Client.objects.get(install_id=install_id)
            detection = create_detection(asset, client, source)
            enqueue_detection_task(detection)
            created = True

        response_serializer = self.get_serializer(detection)
        response_status = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
        return Response(
            response_serializer.data,
            status=response_status,
        )

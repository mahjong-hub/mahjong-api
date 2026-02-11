import logging

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from user.views import get_install_id
from user.models import Client
from asset.models import Asset
from hand.constants import DetectionStatus, HandSource
from hand.models import HandDetection
from hand.serializers.hand_detection_serializer import HandDetectionSerializer
from hand.services.hand_detection import (
    find_existing_detection,
    create_detection,
)
from hand.services.hand_inference import (
    dispatch_detection,
    process_detection_result,
)
from hand.services.modal_client import poll_detection_result

logger = logging.getLogger(__name__)


class HandDetectionViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for hand detection operations.

    Endpoints:
        POST /hand/detection/
        GET /hand/detection/{id}/
        GET /hand/detection/{id}/poll/
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
            client = Client.objects.get(install_id=install_id)
            detection = create_detection(asset, client, source)
            dispatch_detection(detection)
            created = True

        response_serializer = self.get_serializer(detection)
        response_status = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
        return Response(
            response_serializer.data,
            status=response_status,
        )

    @action(detail=True, methods=['get'])
    def poll(self, request, pk=None):
        """Poll Modal for detection results."""
        detection = self.get_object()

        if detection.status in (
            DetectionStatus.SUCCEEDED.value,
            DetectionStatus.FAILED.value,
        ):
            serializer = self.get_serializer(detection)
            return Response(serializer.data)

        result = poll_detection_result(detection.call_id)

        if result:
            detection = process_detection_result(detection, result)

        serializer = self.get_serializer(detection)
        return Response(serializer.data)

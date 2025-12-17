from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from asset.views import get_install_id
from hand.serializers.detection import (
    DetectionDetailSerializer,
    TriggerDetectionRequestSerializer,
    TriggerDetectionResponseSerializer,
)
from hand.services.detection import get_hand_detection, trigger_hand_detection


class DetectionViewSet(viewsets.ViewSet):
    """
    ViewSet for hand detection operations.

    Endpoints:
        POST /hand/detect/
        GET /hand/detect/{hand_detection_id}/
    """

    def create(self, request: Request) -> Response:
        """Trigger detection on an uploaded asset."""
        install_id = get_install_id(request)

        serializer = TriggerDetectionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = trigger_hand_detection(
            asset_id=serializer.validated_data['asset_id'],
            install_id=install_id,
            source=serializer.validated_data.get('source'),
        )

        response_serializer = TriggerDetectionResponseSerializer(
            instance={
                'hand_id': result.hand_id,
                'asset_ref_id': result.asset_ref_id,
                'hand_detection_id': result.hand_detection_id,
                'status': result.status,
            },
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request: Request, pk: str) -> Response:
        """Get detection status and results."""
        install_id = get_install_id(request)

        detection = get_hand_detection(
            hand_detection_id=pk,
            install_id=install_id,
        )

        response_serializer = DetectionDetailSerializer(instance=detection)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

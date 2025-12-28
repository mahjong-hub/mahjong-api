from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from asset.views import get_install_id
from hand.models import HandDetection
from hand.serializers.hand_detection_serializer import HandDetectionSerializer


class HandDetectionViewSet(
    mixins.CreateModelMixin,
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        detection = serializer.save()

        response_serializer = self.get_serializer(detection)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

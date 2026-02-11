from rest_framework import mixins, viewsets

from user.views import get_install_id
from hand.models import HandDetection
from hand.serializers.hand_detection_serializer import HandDetectionSerializer


class HandDetectionViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for hand detection operations.

    Endpoints:
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

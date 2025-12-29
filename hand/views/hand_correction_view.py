from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from user.views import get_install_id
from hand.filters import HandCorrectionFilter
from hand.models import HandCorrection
from hand.serializers.hand_correction_serializer import (
    HandCorrectionSerializer,
)


class HandCorrectionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for hand correction operations.

    Endpoints:
        POST /hand/correction/
        GET /hand/correction/
        GET /hand/correction/{id}/
    """

    serializer_class = HandCorrectionSerializer
    filterset_class = HandCorrectionFilter

    def get_queryset(self):
        """Filter corrections by client ownership."""
        install_id = get_install_id(self.request)
        queryset = (
            HandCorrection.objects.filter(hand__client__install_id=install_id)
            .select_related('hand', 'detection')
            .order_by('-created_at')
        )

        # Prefetch tiles for retrieve action
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('tiles')

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['install_id'] = get_install_id(self.request)
        return context

    def create(self, request, *args, **kwargs):
        """Create a new correction for a hand."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        correction = serializer.save()

        # Re-serialize for response with all fields
        response_serializer = self.get_serializer(correction)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

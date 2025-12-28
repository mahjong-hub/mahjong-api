import django_filters

from hand.models import HandCorrection


class HandCorrectionFilter(django_filters.FilterSet):
    """Filter for HandCorrection list endpoint."""

    hand_id = django_filters.UUIDFilter(field_name='hand_id')

    class Meta:
        model = HandCorrection
        fields = ['hand_id']

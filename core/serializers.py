from rest_framework import serializers


class ReadOnlyMixin:
    def to_internal_value(self, data):
        raise NotImplementedError('This serializer is read-only.')


class ReadOnlyModelSerializer(
    ReadOnlyMixin,
    serializers.ModelSerializer,
):
    """A read-only ModelSerializer."""

    pass

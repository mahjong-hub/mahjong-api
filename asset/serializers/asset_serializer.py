from rest_framework import serializers

from asset.models import Asset


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer for Asset model.

    Used for both presign and complete upload responses.
    """

    upload_session_id = serializers.UUIDField(
        source='upload_session.id',
        read_only=True,
    )

    class Meta:
        model = Asset
        fields = [
            'upload_session_id',
            'id',
            'storage_key',
            'is_active',
            'byte_size',
            'checksum',
        ]
        read_only_fields = fields

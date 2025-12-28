from rest_framework import serializers

from asset.models import Asset
from hand.constants import HandSource
from hand.models import DetectionTile, HandDetection
from hand.services.hand_detection import trigger_hand_detection


class DetectionTileSerializer(serializers.ModelSerializer):
    """Serializer for detection tiles."""

    class Meta:
        model = DetectionTile
        fields = [
            'tile_code',
            'x1',
            'y1',
            'x2',
            'y2',
            'confidence',
        ]


class HandDetectionSerializer(serializers.ModelSerializer):
    """
    Serializer for hand detections.

    For create: expects `install_id` in context, accepts asset_id, source.
    For read: returns all fields including nested tiles.
    """

    tiles = DetectionTileSerializer(many=True, read_only=True)
    asset_ref_id = serializers.UUIDField(source='asset_ref.id', read_only=True)

    # Write-only for create
    asset_id = serializers.UUIDField(write_only=True)
    source = serializers.ChoiceField(
        choices=HandSource.choices(),
        default=HandSource.CAMERA.value,
        write_only=True,
    )

    class Meta:
        model = HandDetection
        fields = [
            'id',
            'hand_id',
            'asset_id',
            'asset_ref_id',
            'source',
            'status',
            'model_name',
            'model_version',
            'confidence_overall',
            'tiles',
            'error_code',
            'error_message',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'hand_id',
            'asset_ref_id',
            'status',
            'model_name',
            'model_version',
            'confidence_overall',
            'tiles',
            'error_code',
            'error_message',
            'created_at',
        ]

    def validate_asset_id(self, value):
        """Validate asset exists, is active, and belongs to client."""
        install_id = self.context.get('install_id')

        try:
            asset = Asset.objects.select_related('upload_session__client').get(
                id=value,
            )
        except Asset.DoesNotExist:
            raise serializers.ValidationError('Asset not found.') from None

        if install_id and (
            not asset.upload_session
            or asset.upload_session.client.install_id != install_id
        ):
            raise serializers.ValidationError(
                'Asset does not belong to this client.',
            )

        if not asset.is_active:
            raise serializers.ValidationError(
                'Asset is not active. Complete upload first.',
            )

        self._asset = asset
        return value

    def create(self, validated_data) -> HandDetection:
        """Create via service layer (handles Hand, AssetRef, Detection creation)."""
        install_id = self.context.get('install_id')

        result = trigger_hand_detection(
            asset_id=validated_data['asset_id'],
            install_id=install_id,
            source=validated_data.get('source', HandSource.CAMERA.value),
        )

        return (
            HandDetection.objects.select_related('asset_ref')
            .prefetch_related('tiles')
            .get(
                id=result.hand_detection_id,
            )
        )

from rest_framework import serializers

from hand.models import Hand, HandCorrection, HandDetection, HandTile
from hand.services.hand_correction import TileInput, create_hand_correction
from hand.tiles import TileCode


class HandTileSerializer(serializers.ModelSerializer):
    """Serializer for hand tiles."""

    tile_code = serializers.ChoiceField(choices=TileCode.choices())

    class Meta:
        model = HandTile
        fields = ['tile_code', 'sort_order']


class HandCorrectionSerializer(serializers.ModelSerializer):
    """
    Serializer for hand corrections.

    For create: expects `install_id` in context, accepts hand_id, detection_id, tiles.
    For read: returns all fields including computed is_active.
    """

    is_active = serializers.SerializerMethodField()
    tiles = HandTileSerializer(many=True)
    created_at = serializers.DateTimeField(read_only=True)

    # Write-only for create
    hand_id = serializers.UUIDField(write_only=True)
    detection_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        default=None,
    )

    class Meta:
        model = HandCorrection
        fields = [
            'id',
            'hand_id',
            'detection_id',
            'tiles',
            'is_active',
            'created_at',
        ]

    def get_is_active(self, obj) -> bool:
        """Check if this correction is the active one for its hand."""
        if not hasattr(obj, 'hand') or obj.hand is None:
            return False
        return obj.hand.active_hand_correction_id == obj.id

    def validate_hand_id(self, value):
        """Validate hand exists and belongs to client."""
        install_id = self.context.get('install_id')
        if not install_id:
            return value

        try:
            hand = Hand.objects.select_related('client').get(id=value)
        except Hand.DoesNotExist:
            raise serializers.ValidationError('Hand not found.') from None

        if hand.client.install_id != install_id:
            raise serializers.ValidationError(
                'Hand does not belong to this client.',
            ) from None

        self._hand = hand
        return value

    def validate_detection_id(self, value):
        """Validate detection exists if provided."""
        if value is None:
            return None

        try:
            detection = HandDetection.objects.get(id=value)
        except HandDetection.DoesNotExist:
            raise serializers.ValidationError('Detection not found.') from None

        self._detection = detection
        return value

    def create(self, validated_data) -> HandCorrection:
        """Create via service layer (handles tiles and business logic)."""
        tiles = [
            TileInput(
                tile_code=tile['tile_code'],
                sort_order=tile['sort_order'],
            )
            for tile in validated_data['tiles']
        ]

        return create_hand_correction(
            hand=self._hand,
            tiles=tiles,
            detection=getattr(self, '_detection', None),
        )

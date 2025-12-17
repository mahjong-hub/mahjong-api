from rest_framework import serializers

from hand.constants import DetectionStatus, HandSource


class TriggerDetectionRequestSerializer(serializers.Serializer):
    asset_id = serializers.UUIDField(
        required=True,
        help_text='Asset ID to run detection on',
    )
    source = serializers.ChoiceField(
        required=False,
        choices=HandSource.choices(),
        default=HandSource.CAMERA.value,
        help_text='Source of the hand image',
    )


class TriggerDetectionResponseSerializer(serializers.Serializer):
    hand_id = serializers.UUIDField()
    asset_ref_id = serializers.UUIDField()
    hand_detection_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=DetectionStatus.choices())


class DetectionTileSerializer(serializers.Serializer):
    tile_code = serializers.CharField()
    x1 = serializers.IntegerField()
    y1 = serializers.IntegerField()
    x2 = serializers.IntegerField()
    y2 = serializers.IntegerField()
    confidence = serializers.DecimalField(max_digits=5, decimal_places=4)


class DetectionDetailSerializer(serializers.Serializer):
    hand_detection_id = serializers.UUIDField(source='id')
    hand_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=DetectionStatus.choices())
    model_name = serializers.CharField()
    model_version = serializers.CharField()
    confidence_overall = serializers.DecimalField(
        max_digits=5,
        decimal_places=4,
        allow_null=True,
    )
    tiles = DetectionTileSerializer(many=True)
    error_code = serializers.CharField(allow_blank=True)
    error_message = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()

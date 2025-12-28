from rest_framework import serializers

from asset.constants import ALLOWED_IMAGE_MIMES, UploadPurpose


class PresignRequestSerializer(serializers.Serializer):
    """Request serializer for presigned upload."""

    content_type = serializers.ChoiceField(
        required=True,
        choices=[(m, m) for m in sorted(ALLOWED_IMAGE_MIMES)],
        help_text='MIME type of the file to upload',
    )
    purpose = serializers.ChoiceField(
        required=False,
        choices=UploadPurpose.choices(),
        default=UploadPurpose.HAND_PHOTO.value,
        help_text='Purpose of the upload',
    )

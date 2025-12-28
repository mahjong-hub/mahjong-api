from rest_framework import serializers

from user.models import Client


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for client identity.

    For create (identify): accepts install_id and optional label.
    For read: returns all client fields.
    """

    install_id = serializers.CharField(
        max_length=64,
        help_text='Unique device/app install identifier',
    )
    label = serializers.CharField(
        required=False,
        max_length=120,
        default='',
        allow_blank=True,
        help_text='Optional device label/name',
    )

    class Meta:
        model = Client
        fields = ['install_id', 'label', 'created_at', 'last_seen_at']
        read_only_fields = ['created_at', 'last_seen_at']

    def create(self, validated_data) -> Client:
        """
        Get or create a client by install_id and update last_seen_at.

        If the client exists, updates last_seen_at.
        If the client doesn't exist, creates a new one.
        """
        install_id = validated_data['install_id']
        label = validated_data.get('label', '')

        client, created = Client.objects.get_or_create(
            install_id=install_id,
            defaults={'label': label},
        )

        if not created:
            client.touch()
            if label and label != client.label:
                client.label = label
                client.save(update_fields=['label'])

        return client

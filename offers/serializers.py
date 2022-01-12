from rest_framework.serializers import ModelSerializer

from core import models


class OfferSerializer(ModelSerializer):
    """Serializer for Offer model"""

    class Meta:
        model = models.Offer
        fields = ('id', 'title', 'percentage', 'desc', 'created_on', 'expiry_date')
        read_only_fields = ('id', 'created_on')
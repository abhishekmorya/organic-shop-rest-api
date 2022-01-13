from rest_framework.serializers import ModelSerializer

from core import models


class PaymentModeSerializer(ModelSerializer):
    """Serializer for payment mode Api"""

    class Meta:
        model = models.PaymentMode
        fields = ('id', 'title', 'desc', 'charges', 'enabled', 'created_on')
        read_only_fields = ('id', 'created_on')

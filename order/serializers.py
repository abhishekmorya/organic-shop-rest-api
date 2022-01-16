from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from core import models
from shopping.serializers import ShoppingDetailSerializer
from offers.serializers import OfferSerializer

class PaymentModeSerializer(ModelSerializer):
    """Serializer for payment mode Api"""

    class Meta:
        model = models.PaymentMode
        fields = ('id', 'title', 'desc', 'charges', 'enabled', 'created_on')
        read_only_fields = ('id', 'created_on')


class OrderSerializer(ModelSerializer):
    """Serializer for order api"""
    cartItems = PrimaryKeyRelatedField(
        many = True,
        queryset = models.ShoppingCart.objects.all()
    )

    offers_applied = PrimaryKeyRelatedField(
        many = True,
        queryset = models.Offer.objects.all()
    )

    class Meta:
        model = models.Order
        fields = ('id', 'cartItems', 'offers_applied', 'ordered_on', 'shipping_address', 'billing_address', 'payment_mode')
        read_only_fields = ('id', 'ordered_on',)
    

class OrderDetailSerializer(OrderSerializer):
    """Serializer for detailed order"""
    cartItems = ShoppingDetailSerializer(many = True, read_only = True)
    offers_applied = OfferSerializer(many = True, read_only = True)
    payment_mode = PaymentModeSerializer(read_only = True)
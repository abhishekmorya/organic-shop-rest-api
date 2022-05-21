from rest_framework.serializers import ModelSerializer

from core import models
from product.serializers import ProductDetailSerializer


class ShoppingSerializer(ModelSerializer):
    """Serializer class for Shopping Cart model"""

    class Meta:
        """Meta class for Shopping serializer"""
        model = models.ShoppingCart
        fields = ('id', 'product', 'count')
        read_only_fields = ('id',)


class ShoppingDetailSerializer(ShoppingSerializer):
    """Serializer for detailed shopping cart"""

    product = ProductDetailSerializer(read_only = True)

class SessionShoppingSerializer(ModelSerializer):
    """Serializer for Session objects of shopping cart"""

    class Meta:
        model = models.SessionShoppingCart
        fields = ('id', 'product', 'count')
        read_only_fields = ('id', )

class SessionShoppingDetailSerializer(SessionShoppingSerializer):
    """Serializer for detail Session Shopping cart"""

    product = ProductDetailSerializer(read_only = True)
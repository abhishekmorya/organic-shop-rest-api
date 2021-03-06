from rest_framework import serializers
from core.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    class Meta:
        model = Category
        fields = ('id', 'name', 'desc', 'created_date')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""

    class Meta:
        model = Product
        fields = ('id', 'title', 'category', 'desc',
                  'created_date', 'price', 'quantity', 'unit', 'image')
        read_only_fields = ('id',)


class ProductDetailSerializer(ProductSerializer):
    """Serializer for detailed Product"""

    category = CategorySerializer(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for image field of product object"""

    class Meta:
        model = Product
        fields = ('id', 'image')
        read_only_fields = ('id',)
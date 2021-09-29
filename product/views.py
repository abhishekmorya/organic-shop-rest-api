from django.http import HttpResponse

from rest_framework import viewsets, authentication

from core import permissions
from core import models
from product import serializers

def greet(request):
    """Greet message"""
    return HttpResponse("Hello!")


class CategoryView(viewsets.ModelViewSet):
    """Category by View"""
    serializer_class = serializers.CategorySerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsStaffOrReadOnly,)
    queryset = models.Category.objects.all()

    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)


class ProductView(viewsets.ModelViewSet):
    """Viewset for Product object"""

    serializer_class = serializers.ProductSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsStaffOrReadOnly,)
    queryset = models.Product.objects.all().order_by('id')

    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)

    def get_queryset(self):
        """Customized queryset for filtering by category feature"""
        cates = self.request.query_params.get('categories')
        queryset = self.queryset.all().order_by('id')
        if cates:
            categories = [int(c) for c in cates.split(',')]
            queryset = models.Product.objects.filter(category__in = categories)
        return queryset

    def get_serializer_class(self):
        """Return detail serializer for retrieve action"""
        if self.action == 'retrieve':
            return serializers.ProductDetailSerializer
        return self.serializer_class
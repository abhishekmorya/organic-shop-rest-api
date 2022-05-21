import os
from django.http import HttpResponse
from django.conf import settings

from rest_framework import status, viewsets, authentication
from rest_framework.decorators import action
from rest_framework.response import Response

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
        # self.request.session['username'] = self.request.user.get_email_field_name()
        return serializer.save(user = self.request.user)

    def get_queryset(self):
        """Customized queryset for filtering by category feature"""
        cates = self.request.query_params.get('categories')
        queryset = self.queryset.all().order_by('id')
        # print('session_key: ' + self.request.session.session_key)
        if cates:
            categories = [int(c) for c in cates.split(',')]
            queryset = models.Product.objects.filter(category__in = categories)
        return queryset

    def get_serializer_class(self):
        """Return detail serializer for retrieve action"""
        if self.action == 'retrieve':
            return serializers.ProductDetailSerializer
        if self.action == 'upload_image':
            return serializers.ProductImageSerializer
        return self.serializer_class

    @action(methods = ['POST'], detail = True, url_path='upload-image')
    def upload_image(self, request, pk = None):
        """Upload image to product"""
        product = self.get_object()
        serializer = self.get_serializer(
            product,
            data = request.data
        )

        if serializer.is_valid():
            image = self.queryset.get(pk = product.id).image
            if image:
                old_image_path = os.path.join(settings.MEDIA_ROOT, image.path)
                os.remove(old_image_path)
            serializer.save()
            return Response(
                serializer.data,
                status = status.HTTP_200_OK 
            )
        
        return Response(
            serializer.errors,
            status = status.HTTP_400_BAD_REQUEST 
        )
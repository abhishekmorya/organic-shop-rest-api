from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from core import models

from shopping import serializers

class ShoppingView(viewsets.ModelViewSet):
    """Viewset for Shopping object"""
    serializer_class = serializers.ShoppingSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.ShoppingCart.objects.all().order_by('id')

    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ShoppingDetailSerializer
        return self.serializer_class


class SessionShoppingView(viewsets.ModelViewSet):
    """Viewset for Session Shopping object"""
    serializer_class = serializers.SessionShoppingSerializer
    queryset = models.SessionShoppingCart.objects.all().order_by('id')

    def perform_create(self, serializer):
        session_key = self.request.session.session_key
        return serializer.save(aUser = session_key)
    
    def get_queryset(self):
        session_key = self.request.session.session_key
        return self.queryset.filter(aUser = session_key)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.SessionShoppingDetailSerializer
        return self.serializer_class
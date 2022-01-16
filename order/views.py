from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core import models
from order import serializers
from core.permissions import IsStaffOrAuthenticated


class PaymentModeView(ModelViewSet):
    """View for payment mode"""
    serializer_class = serializers.PaymentModeSerializer
    permission_classes = (IsStaffOrAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = models.PaymentMode.objects.all().order_by('-id')

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class OrderView(GenericViewSet,
                mixins.CreateModelMixin,
                mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin):
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = models.Order.objects.all().order_by('-id')

    def get_queryset(self):
        if self.request.user.is_staff == False:
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.OrderDetailSerializer
        return self.serializer_class

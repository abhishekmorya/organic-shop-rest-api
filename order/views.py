from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
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
        return serializer.save(user = self.request.user)

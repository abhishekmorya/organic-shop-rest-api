from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from core.models import Offer
from offers import serializers
from core import permissions


class OfferView(viewsets.ModelViewSet):
    """Viewset for Offer api"""

    serializer_class = serializers.OfferSerializer
    permission_classes = (permissions.IsStaffOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = Offer.objects.all().order_by('-id')

    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)

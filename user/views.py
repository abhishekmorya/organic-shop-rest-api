from core.models import UserAddress, UserDetails
from rest_framework import generics, mixins, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import viewsets

from user import serializers


class CreateUserView(generics.CreateAPIView):
    """View for create a new user"""

    serializer_class = serializers.UserSerializer


class UserTokenView(ObtainAuthToken):
    """View to obtain auth token for authenticated user"""

    serializer_class = serializers.UserTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    """View for retrieve and update the user for authentiated user"""

    serializer_class = serializers.UserSerializer
    authentication_classes = [authentication.TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]

    def get_object(self):
        """Retrieve and return authenticated user"""

        return self.request.user


class UserAddressView(viewsets.ModelViewSet):
    """Viewset for UserAddress object"""

    serializer_class = serializers.UserAddressSerializer
    authentication_classes = [authentication.TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]
    queryset = UserAddress.objects.all()

    def get_queryset(self):
        
        return self.queryset.filter(
            user = self.request.user
        )
    
    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)


class UserDetailsView(viewsets.GenericViewSet,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin):
    """Viewset for UserDetails viewset"""
    serializer_class = serializers.UserDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    queryset = UserDetails.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            user = self.request.user
        )

    def perform_create(self, serializer):
        
        return serializer.save(user = self.request.user)
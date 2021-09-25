from rest_framework import generics, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

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
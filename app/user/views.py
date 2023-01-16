"""
views for the user api
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    # create a new user in the system
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    # create a new auth token for user

    # override to use email instead of default username
    serializer_class = AuthTokenSerializer

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # optional


class ManageUserView(generics.RetrieveUpdateAPIView):
    # manage the authenticated user

    serializer_class = UserSerializer

    # who is this user?
    authentication_classes = [authentication.TokenAuthentication]

    # what is this user allowed to do?
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # retrieve and return the authenticated user
        return self.request.user

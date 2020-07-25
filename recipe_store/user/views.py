from rest_framework import generics
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
# Create your views here.


class CreateUserView(generics.CreateAPIView):
    """Creates a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Creates a new auth token for user"""
    serializer_class = AuthTokenSerializer
    # set the renderer class, so that we can view the endpoint in browser
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

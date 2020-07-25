from rest_framework import generics, authentication, permissions
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


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manages view/update for authenticated user"""
    serializer_class = UserSerializer
    # 2 more class variablesfor authenticationand Permissions
    # authentication could be cookie authentication but we are using token authentication
    authentication_classes = {authentication.TokenAuthentication, }
    # Permission level of access that the user can have : only needs to be logged in here
    permission_classes = {permissions.IsAuthenticated, }
    # get the model for the logged in authenticated user

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user

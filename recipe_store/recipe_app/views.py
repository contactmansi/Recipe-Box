from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe_app import serializers
# add custome action to viewset
from rest_framework.decorators import action
# to return custom response
from rest_framework.response import Response
# Mixis help customise the List/Create fucnionality available with viewsets


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base ViewSet for user owned recipe attributes: Tag and Ingredient"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return tags for current authenticated user only
        When viewset is invoked from url, it'll call queryset to retrive the tags/ingredient"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """View/Create ingredients in the databse"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet, mixins.ListModelMixin):
    """Manage recipes in the database - using ModelViewset to provide all CRUD options"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.RecipeSerializer

    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        # Override function - get_serializer_class
        # change the serializer class for differennt actions available with viewsets
        # self object also contains the action being used for current request
        # customize the response to generate a detailed recipe response with ingredients and tags details
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Save the newly created recipe"""
        serializer.save(user=self.request.user)

    # actionas are defined as functions to the viewsets,
    # by default we have overriden get_queryset, get_serializer_class, perform_create
    # define a custom action: 1. using @action() decorator, 2. methods = to post an image to our recipe
    # detail - says that this action is for detail recipe, using detail_url for existing recipe
    # url_path = 'upload-image': USE url recipe/{id}/upload-image
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        # retrieve the recipe object that is being accessed in the url based on the id
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# class TagViewSet(viewsets.GenericViewSet,
#                  mixins.ListModelMixin,
#                  mixins.CreateModelMixin):
#     """Manage tags in the database"""
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     # Queryset to be returned
#     queryset = Tag.objects.all()
#     serializer_class = serializers.TagSerializer
#
#     def get_queryset(self):
#         """Return tags for current authenticated user only
#         When viewset is invoked from url, it'll call queryset to retrive the tags"""
#         return self.queryset.filter(user=self.request.user).order_by('-name')
#
#     def perform_create(self, serializer):
#         """Create a new tag"""
#         serializer.save(user=self.request.user)
#
#
# class IngredientViewSet(viewsets.GenericViewSet,
#                         mixins.ListModelMixin,
#                         mixins.CreateModelMixin):
#     """View/Create ingredients in the databse"""
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     serializer_class = serializers.IngredientSerializer
#
#     queryset = Ingredient.objects.all()
#
#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user).order_by('-name')
#
#     def perform_create(self, serializer):
#         """Create a new ingredient"""
#         serializer.save(user=self.request.user)

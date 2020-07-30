from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe  # , Ingredient  # , Tag
from recipe_app.serializers import RecipeSerializer  # , IngredientSerializer

RECIPES_URL = reverse('recipe_app:recipe-list')

# ** with params converts the extra parameters into a dictonary


def sample_recipe(user, **params):
    """Helper function to easily create sample recipes for testing.
    New Method for helper functions: When we need repeated recipe objects in our tests and
    the recipe has 4 reqd parameters - setup this fucntion to create a recipe with
    default values, so we don't need to specify these defaults everytime we create a new recipe"""
    # defailts: dict for required recipe parameters with values
    defaults = {
        'title': 'Sample Red Sauce Pasta',
        'time_minutes': 15,
        'price': 3.50,
    }
    # **params can override the defaults when required using update() in python dict()
    # can also add additional parameters to defaults if not present already
    defaults.update(params)
    # ** with defaults in function call converts dictionary to parameters
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Tests for non-authenticated recipe endpoints"""

    def setUp(self):
        """Tasks to be done for public tests"""
        self.client = APIClient()

    def test_login_required(self):
        """Test unauthenticated requests for recipe api are unauthorized"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Tests for authenticatedrecipe based endpoints"""

    def setUp(self):
        """Tasks to do before running the private tests"""
        self.user = get_user_model().objects.create_user(
            email='testrecipe@gmail.com',
            password='testrecipe',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list_ordered_by_title(self):
        """Test retrieving recipe list ordered by ID for authenticated user only"""
        # Ingredient.objects.create(user=self.user, name='Salt')
        # Ingredient.objects.create(user=self.user, name='Penne')
        # # italian = Tag.objects.create(user=self.user, name='Italian')
        # ingredients = Ingredient.objects.all().order_by('-name')

        sample_recipe(self.user)  # , **IngredientSerializer(ingredients, many=True).data)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieved_recipes_for_authenticated_user_only(self):
        """Test recipes for other only authenticated user are returned"""
        new_user = get_user_model().objects.create_user(
            email='new_user@gmail.com', password='new_user'
        )
        sample_recipe(new_user)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

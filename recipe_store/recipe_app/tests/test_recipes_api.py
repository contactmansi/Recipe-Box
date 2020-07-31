from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient, Tag
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer  # , IngredientSerializer

RECIPES_URL = reverse('recipe_app:recipe-list')


def recipe_detail_url(recipe_id):
    """Return the recipe deatils URL
    # Helper function to create urls with argument ID for ehich details are to be retrieved
    # List recipes list : /recipe/recipes
    # Detail display of one recipe: /recipe/recipes/1"""
    return reverse('recipe_app:recipe-detail', args=[recipe_id, ])


def sample_ingredient(user, name='Chilli Sauce'):
    return Ingredient.objects.create(user=user, name=name)


def sample_tag(user, name='Main Course'):
    """Helper function to create sample tags"""
    return Tag.objects.create(user=user, name=name)


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
        sample_recipe(self.user)
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

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        # Access tags/ingredients using many to many relationship like this
        recipe.tags.add(sample_tag(user=self.user))
        recipe.tags.add(sample_tag(user=self.user, name='Italian'))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Create a basic recipe with required parameters"""
        payload = {
            'title': 'Pizza',
            'price': 3.00,
            'time_minutes': 20
        }

        res = self.client.post(RECIPES_URL, payload)

        # recipe_exists = Recipe.objects.filter(user=self.user).exists()
        # self.assertTrue(recipe_exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test Creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Cheese Cake',
            'tags': [tag1.id, tag2.id, ],
            'time_minutes': 20,
            'price': 10,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipes with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Olives')
        ingredient2 = sample_ingredient(user=self.user, name='Broccoli')
        payload = {
            'title': 'Salad',
            'price': 15,
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingreditents = recipe.ingredients.all()

        self.assertEqual(ingreditents.count(), 2)
        self.assertIn(ingredient1, ingreditents)
        self.assertIn(ingredient2, ingreditents)

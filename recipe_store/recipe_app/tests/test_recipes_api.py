from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient, Tag
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer  # , IngredientSerializer
# image library for python - let's us create test images to upload to api
from PIL import Image
# python function allows us to generate temporary files on the system
import tempfile
import os

RECIPES_URL = reverse('recipe_app:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe_app:recipe-upload-image', args=[recipe_id, ])


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

    # PATCH used to update fields that are provided in the payload
    # PUT
    def test_partial_update_recipe(self):
        """Test updating recipe with patch"""
        # Create a sample recipe to be updated later
        recipe = sample_recipe(user=self.user)
        # Add a tag to the sample recipe
        recipe.tags.add(sample_tag(user=self.user))
        # Create a new tag to be added to sample recipe later
        new_tag = sample_tag(user=self.user, name="Curry")
        # Payload to be used to update the recipe with new_tag replacing the old one
        payload = {'title': 'Paneer Tikka', 'tags': [new_tag.id]}
        # use detailed url with payload for updating requests - important
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)
        # After patch/put request - Refreshes the values in the DB - important
        recipe.refresh_from_db()
        # Check change in title name from defailt Sample_recipe to Chicken Tikka
        self.assertEqual(recipe.title, payload['title'])
        # Check no. of tags is one only, new replaced by old
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)  # length is same as count()
        # Check the new_tag is an entry in the recipe's tags queryset
        self.assertIn(new_tag, tags)

    def test_full_recipe_update(self):
        """Test updating a recipe with PUT request"""
        # Expected: Replace the old recipe obj with new recipe obj
        # Fields removed in the payload will be remved from new recipe
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        # New recipe payload with new name, price, time_minutes, no tags
        payload = {
            'title': 'Pizza',
            'price': 3.50,
            'time_minutes': 45,
        }
        url = recipe_detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testrecipeimage@gmail.com',
            password='testrecipeimage',
        )
        self.client.force_authenticate(self.user)
        # create a sample_recipe for testing the image upload
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """ tearDown() Runs after the tests are run - clearing testing images"""
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading image to recipe successfully"""
        url = image_upload_url(self.recipe.id)
        # USe context manager to create a temp file in the system, suffix = extension
        # coz we need the name of the temp file so use NamedTemporaryFile
        # after exiting the context manager that file is deleted automatically
        # Process: create a NTF, write an image to that file, upload that file through API
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # set pointer back to the beginning of file using seek
            ntf.seek(0)
            # tell django to make a multipart form request not json(by default)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertTrue(os.path.exists(self.recipe.image.path))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test returning recieps with specific tags"""
        recipe1 = sample_recipe(user=self.user, title="Recipe 1")
        recipe2 = sample_recipe(user=self.user, title='Recipe 2')
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title="Recipe 3")

        res = self.client.get(
            RECIPES_URL,
            {'tags': f'{tag1.id}, {tag2.id}'}
        )
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes filtered by ingredients"""
        recipe1 = sample_recipe(user=self.user, title='Recipe 1')
        recipe2 = sample_recipe(user=self.user, title='Recipe 2')
        recipe3 = sample_recipe(user=self.user, title='Recipe 3')
        ingredient1 = sample_ingredient(user=self.user, name='Ingredient 1')
        ingredient2 = sample_ingredient(user=self.user, name='Ingredient 2')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

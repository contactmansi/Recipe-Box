from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe_app.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe_app:ingredient-list')


class PublicIngredientAPITests(TestCase):
    """Test publically available Ingredients APIs"""

    def setUp(self):
        """Setup client only"""
        self.client = APIClient()

    def test_user_login_required(self):
        """Test user login is required to access the ingredient apis endpoints"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authorized user's Ingredients api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='testpass',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving ingredients returns ingredients list by name"""
        Ingredient.objects.create(user=self.user, name='Penne')
        Ingredient.objects.create(user=self.user, name='Olives')

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieved_ingredients_for_authenticated_user_only(self):
        """Test retrived ingredients for the currently authenticated user only, not other users"""

        new_user = get_user_model().objects.create_user(
            email='new_user@gmail.com', password='new_user_password'
        )
        Ingredient.objects.create(user=new_user, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Penne')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(len(res.data), 1)

    def test_create_ingredient_successfully(self):
        """Test created ingredient successfully for logged in user"""
        # payload -> make a POST request -> Verify ingredient exists for user
        payload = {'name': 'Pepper'}
        self.client.post(INGREDIENTS_URL, payload)

        ingredients_exist = Ingredient.objects.filter(
            user=self.user, name=payload['name']
        ).exists()
        self.assertTrue(ingredients_exist)

    def test_create_ingredient_invalid(self):
        """Test no ingredient created for wrong payload"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

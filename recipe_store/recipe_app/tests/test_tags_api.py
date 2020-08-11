from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe_app.serializers import TagSerializer

TAGS_URL = reverse('recipe_app:tag-list')


class PublicTagsApiTests(TestCase):
    """Test publically available tags APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for test"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authorized user tags api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com', 'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags returns list ordered by name
        setup sample tags, make requests -> assert what was expected"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        # make a request to the tags url -> Expected to return all tags
        res = self.client.get(TAGS_URL)
        # Query the model to get the expected result
        # ExpectedResult - Tags are returned in reverse alphabetical order by name
        tags = Tag.objects.all().order_by('-name')
        # Serialize our tags object with multiple tags - pass namy = true
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tags_only_for_authenticated_user(self):
        """Test tags returned are for authenticated user and not others
        Create a new user other than setup so that the tag for this user is not
        in response, since this new was not authenticated"""

        new_user = get_user_model().objects.create_user(
            'new_user@gmail.com', 'new_password',
        )
        Tag.objects.create(user=new_user, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check the length of results returned expected = 1 for authenticated self.user, 2 will be wrong
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        # payload -> make a request -> Verify tag created
        payload = {'name': 'Beverage'}
        self.client.post(TAGS_URL, payload)

        tags_exists = Tag.objects.filter(
            user=self.user, name=payload['name']
        ).exists()

        self.assertTrue(tags_exists)

    def test_create_invalid_tag_fails(self):
        """Test creating a new tag with invaid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test filtering tags by those assigned to recipe"""
        tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        tag2 = Tag.objects.create(user=self.user, name='Tag 2')
        recipe = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=5.00,
            user=self.user
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returned uniques items"""
        tag = Tag.objects.create(user=self.user, name='Tag 1')
        # unassigned tag, to check the length of the res.data in assertions
        Tag.objects.create(user=self.user, name='Tag 2')
        recipe1 = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Recipe 2',
            time_minutes=10,
            price=15.00,
            user=self.user
        )
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

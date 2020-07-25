from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# rest framework test helper tools
from rest_framework.test import APIClient
from rest_framework import status

# Caps is naming convention for variables u dont expect t change
CREATE_USER_URL = reverse('user:create')
# url for the http request to generate our token
TOKEN_URL = reverse('user:token')

# Helper function to create a user every time user is needed for test


def create_user(**params):
    return get_user_model().objects.create_user(**params)

# Public APIs are the non-authenticated apis


class PublicUserApiTests(TestCase):
    """Test the public users API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Create user with valid payload is successful"""
        # sample payload
        payload = {
            'email': 'agarwalmansi2911@gmail.com',
            'password': 'testpass',
            'name': 'Test name',
        }
        # make our request
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test creating a duplicate user"""
        payload = {
            'email': 'agarwalmansi2911@gmail.com', 'password': 'testpass',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test that a token is created for user"""
        payload = {
            'email': 'agarwalmansi2911@gmail.com', 'password': 'testpass',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Test that token is not created if invalid credentials are given"""
        create_user(email='agarwalmansi2911@gmail.com', password='testpass')
        payload = {'email': 'agarwalmansi2911@gmail.com', 'password': 'wrong', }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            'email': 'agarwalmansi2911@gmail.com',
            'password': 'testpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

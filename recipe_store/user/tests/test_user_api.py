from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# rest framework helper tools for testing
from rest_framework.test import APIClient
from rest_framework import status

# Caps is naming convention for variables u dont expect to change
CREATE_USER_URL = reverse('user:create')
# url for the http request to generate our token
TOKEN_URL = reverse('user:token')
# endpoint to update and view a specific user details who is already authenticated and logged in
ME_URL = reverse('user:me')

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

    def test_create_token_missing_user_fields(self):
        """Test that email and password are required for generating token"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_is_authenticated_before_retrieving(self):
        """Test that authentication/authorization is required for users"""
        res = self.client.get(ME_URL)
        # make sure that if me url is called w/o authentication then http 401 is returned
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

# private means that authentication is required before running these tests/api


class PrivateUserApiTests(TestCase):
    """Tests for the user api requests that need authentication"""
    # User needs to be created and authenticated before every test

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpassword',
            name='test name'
        )
        # force authenticate the user for testing purpose
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retriving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_request_not_allowed(self):
        """Test HTTP POST request cannot be done on ME_URL, do put/patch only for update"""
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user works"""
        payload = {'name': 'Updated name', 'password': 'updated'}

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

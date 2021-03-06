from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

from unittest.mock import patch


def sample_user(email='test@gmail.com', password='testpass'):
    """helper function : Create sample user during the test"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """ test to create a new user with email is successful"""
        email = 'test@gmail.com'
        password = 'test'
        user = get_user_model().objects.create_user(
            email=email, password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ test the email for a new user is normalized, domain in lower case"""
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email, 'test'
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """test creating user with no email raises a Value error"""
        # anything inside this should raise a value error, if error not raised test fails
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test')

    def test_create_new_superuser(self):
        """test creating a new super user is superuser and staff"""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com', 'test'
        )
        # .is_superuser included as a part of the PermissionsMixin
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the string representation of a tag gives us the name
        When we call the str function on our tag we want it to return
        the name of the tag only - def __str__(): in tag model"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the string representation of a ingredient gives us the name"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test str representation of recipe for required fields only"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='White Sauce Pasta',
            time_minutes=5,
            price=10.00
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')  # uuid4 is a function within uuid
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        # Mock UUID function from the default UUID library that comes with python, imported above
        # Change value of uuid returned by uuid4() to sth like 'tst-uuid', WHY?
        # So that we can reliably test that uuid mactches the mock_uuid, coz don't know what was returned
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        # instance reqd by upload field argument of django models - None here
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        # check file_path is equal to expected path - Literal steing interpolation using f'' strings
        expected_path = f'uploads/images/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)

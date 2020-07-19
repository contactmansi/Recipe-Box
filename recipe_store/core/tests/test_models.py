from django.test import TestCase
from django.contrib.auth import get_user_model


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

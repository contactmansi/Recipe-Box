# Client: helps us to make test requests to our application during unit testing
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
# reverse - allows us to generate url for django admin page


class AdminSiteTests(TestCase):
    # setup function : tasks that need to be done before every tests are run
    # Creating our test Client, New user that we can use to test
    # make sure new user is logged in
    # normal user for listing on admin page
    def setUp(self):
        # sets a client variable to the object
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='admin'
        )
        # Uses the client helper function that allows logging in user using Django authentication
        # no need to manually login the user
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='test',
            name='Test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        # appname : core_user_changelist -> predefined in django admin documentation
        url = reverse('admin:core_user_changelist')
        # Performs a http get on the url given
        res = self.client.get(url)
# response contains the mentioned attribute
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """ User edit page works"""
        # Note how to give arguments with reverse which get appended to the url
        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/1
        res = self.client.get(url)
        # Check page renders okay with res.status_code=200
        self.assertEqual(res.status_code, 200)

    def test_user_add_page(self):
        """ Test Create User page works """
        url = reverse('admin:core_user_add')

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

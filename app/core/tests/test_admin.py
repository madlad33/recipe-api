from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTest(TestCase):
    def setUp(self):
        """Create a super user and log him in
            Create a user"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='test@gmail.com',
            password='1234'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='silent@retreat.com',
            password='1234',
            name='Test user name'
        )


    def test_users_listed(self):
        """Test that users are listed in user page.
        We have to make changes to django admin to accomodate
        ou custom user model"""

        # These urls are listed in django admin docs
        # Gets the URL that lists users in admin page
        # have to register User model to admin for this url to work
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        # AssertContains checks if certain value is present in a dict
        # Also checks if the http respose is OK (200)
        # name field is not available in default UserAdmin class
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=(self.user.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code,200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
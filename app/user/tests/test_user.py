from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
def create_user(**parameter):
    return get_user_model().objects.create_user(**parameter)


class PublicUserApiTests(TestCase):
    """Test the users api(public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Testing created user with a valid payload is successful"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
            'name': 'Test'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Creating a user which already exists"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Check if password too short"""
        payload = {
            'email': 'test@test.com',
            'password': 'pw',
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        """Test that a token is created"""
        payload = {
            'email':'test@test.com',
            'password': 'testpass'
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL,payload)
        self.assertIn('token',response.data)

    def test_create_token_invalid_credentials(self):
        """Test that the token is not created with invalid credentials """
        create_user(email='test@test.com',password='testpass')
        payload = {
            'email':'test@test.com',
            'password':'testwrongpass'
        }
        response = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',response.data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_with_no_user(self):
        """Test that the token is not created if user doesn't exist"""
        payload = {'email':'test@test.com', 'password':'testpass'}
        response = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',response.data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        response = self.client.post(TOKEN_URL,{'email':'one','password':''})
        self.assertNotIn('token',response.data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test that the authentication is required for user"""
        response =self.client.get(ME_URL)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateUserAPITests(TestCase):
    """Test API requests that require authentication"""
    def setUp(self):
      self.user = create_user(
           email='test@test.com',
          password='testpass',
          name='testname'

        )
      self.client = APIClient()
      self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,{
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_not_allowed(self):
        """Test that the post method is not allowed"""
        response = self.client.post(ME_URL)
        self.assertEqual(response.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_update_user_profile(self):
    #     """Testing updating the user profile"""
    #     payload = {'name':'new_name','password':'newpass123' }
    #     response = self.client.patch(ME_URL,payload)
    #     self.user.refresh_from_db()
    #
    #     self.assertEqual(self.user.name, payload['name'])
    #     self.assertTrue(self.user.check_password(payload['password']))
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)


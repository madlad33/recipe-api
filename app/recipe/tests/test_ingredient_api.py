from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredientsAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required"""
        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test the private ingredient API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test1@test.com',
            password='testpass'

        )
        self.client.force_authenticate((self.user))
    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredeint
        """
        Ingredient.objects.create(user=self.user, name='Sugar')
        Ingredient.objects.create(user=self.user, name='Salt')
        response = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serialzier = IngredientSerializer(ingredients,many=True)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,serialzier.data)

    def test_ingredient_limited_to_user(self):
        """Test that only ingredient for the authenticated users are returned"""
        user2 = get_user_model().objects.create_user(
            'test@test1.com',
            'testpass1'
        )
        Ingredient.objects.create(user=user2,name='Vinegar')

        ingredient = Ingredient.objects.create(user=self.user,name='Turmeric')
        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['name'],ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient successful"""
        payload = {'name':'cabbage'}
        self.client.post(INGREDIENT_URL,payload)
        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name'],

        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {
            'name':''
        }
        response = self.client.post(INGREDIENT_URL,payload)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)


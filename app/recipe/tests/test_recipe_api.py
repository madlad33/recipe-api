from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe,Tag,Ingredient
from ..serializers import RecipeSerializer,RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')
def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail',args=[recipe_id])

def sample_recipe(user,**params):
    """Create and return a sample recipe"""
    defaults = {
        'title' : 'Hakka noodles',
        'time_minutes':10,
        'price':5
    }
    defaults.update(params)
    return Recipe.objects.create(user=user,**defaults)

def sample_tag(user,name='main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user,name=name)

def sample_ingredient(user,name='Turmeric'):
    """Return sample ingredient"""
    return Ingredient.objects.create(user=user , name =name)


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated Recipe API access"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that the authentication is required"""
        response = self.client.get(RECIPE_URL)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        """Test retrieving a list of recipe"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by['-id']
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,serializer.data)

    def test_limited_to_user(self):
        """Test retrieving recipe for user"""
        user2 = get_user_model().objects.create(
            'test@testother.com',
            'password'
        )
        sample_recipe(user= user2)
        sample_recipe(user= self.user)
        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data,serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = detail_url(recipe.id)
        response =self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data,serializer.data)


    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title':'Manchurian',
            'time_minutes':40,
            'price':100.00
        }
        response = self.client.post(RECIPE_URL,payload)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key],getattr(recipe,key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user,name='Non Vegan')
        tag2 = sample_tag(user=self.user, name = 'Desert')
        payload = {
            'title':'Pudding',
            'time_minutes':30,
            'price':1000.00,
            'tags':[tag1.id,tag2.id]
        }
        response = self.client.post(RECIPE_URL,payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(),2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)


    def test_create_recipe_with_ingredient(self):
        """Test creating recipe with ingredients"""
        ingredient_1 = sample_ingredient(name='Blackpepper')
        ingredient_2 = sample_ingredient(name = 'Red chilly')
        payload = {
            'title': 'Egg curry',
            'ingredients':[ingredient_1.id,ingredient_2],
            'time_minutes':50,
            'price': 120.00
        }
        response = self.client.post(RECIPE_URL,payload)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(Ingredient.count(),2)
        self.assertIn(ingredient_1,ingredients)
        self.assertIn(ingredient_2,ingredients)


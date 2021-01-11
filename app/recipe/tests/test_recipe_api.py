import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe,Tag,Ingredient
from ..serializers import RecipeSerializer,RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')
def image_upload_url(recipe_id):

    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

        recipes = Recipe.objects.all().order_by('-id',)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,serializer.data)

    def test_limited_to_user(self):
        """Test retrieving recipe for user"""
        user2 = get_user_model().objects.create_user(
            'test33@test.com',
            'testpass'
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

    # def test_create_recipe_with_tags(self):
    #     """Test creating a recipe with tags"""
    #     tag1 = sample_tag(user=self.user,name='Non Vegan')
    #     tag2 = sample_tag(user=self.user, name ='Desert')
    #     payload = {
    #         'title':'Pudding',
    #         'tags': [tag1.id, tag2.id],
    #         'time_minutes':30,
    #         'price':1000.00,
    #
    #     }
    #     response = self.client.post(RECIPE_URL,payload)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     recipe = Recipe.objects.get(id=response.data['id'])
    #     tags = recipe.tags.all()
    #     self.assertEqual(tags.count(),2)
    #     self.assertIn(tag1,tags)
    #     self.assertIn(tag2,tags)


    def test_create_recipe_with_ingredient(self):
        """Test creating recipe with ingredients"""
        ingredient_1 = sample_ingredient(user=self.user,name='Blackpepper')
        ingredient_2 = sample_ingredient(user=self.user,name = 'Red chilly')
        payload = {
            'title': 'Egg curry',
            'ingredients':[ingredient_1.id,ingredient_2.id],
            'time_minutes':50,
            'price': 120.00
        }
        response = self.client.post(RECIPE_URL,payload)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(),2)
        self.assertIn(ingredient_1,ingredients)
        self.assertIn(ingredient_2,ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user,name='curry')
        payload = {
            'title': 'Fried rice',
            'tags':{new_tag.id}
        }
        url = detail_url(recipe.id)
        self.client.patch(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags),1)
        self.assertIn(new_tag,tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title':'Garlic rice',
            'time_minutes':30,
            'price':300.00
        }
        url = detail_url(recipe.id)
        self.client.put(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.time_minutes,payload['time_minutes'])
        self.assertEqual(recipe.price,payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags),0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an email to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title='Fish and chips')

        res = self.client.get(
            RECIPE_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        recipe1 = sample_recipe(user=self.user, title='Posh beans on toast')
        recipe2 = sample_recipe(user=self.user, title='Chicken cacciatore')
        ingredient1 = sample_ingredient(user=self.user, name='Feta cheese')
        ingredient2 = sample_ingredient(user=self.user, name='Chicken')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title='Steak and mushrooms')

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
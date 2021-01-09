from django.test import TestCase
from django.contrib.auth import get_user_model

from .. import models
def sample_user(email='test@test.com',password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):
    def test_create_user_with_email_successfull(self):
        """Test creating a new user with an email is successful"""
        email = 'test@test.com'
        password = 'testpass'
        user = get_user_model().objects.create_user(

            email=email,
            password=password

        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'test@TEST.com'
        user = get_user_model().objects.create_user(email, 'testpass')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpass')

    def test_if_superuser_created(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'testpass'

        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test str representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test string representation"""
        ingredient = models.Ingredient.objects.create(user=sample_user(),name='cucumber')
        self.assertEqual(str(ingredient),ingredient.name)

    def test_recipe_str(self):
        """Test string representation"""
        recipe = models.Recipe.objects.create(user=sample_user(),title='Hakka noodles',time_minutes=30,price=200.00)
        self.assertEqual(str(recipe),recipe.title)

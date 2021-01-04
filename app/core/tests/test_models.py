from django.test import TestCase
from django.contrib.auth import get_user_model


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

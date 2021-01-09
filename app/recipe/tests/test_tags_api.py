from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import SerializerTag

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsAPITest(TestCase):
    """Test the publicly available tags"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is requried for retrieving tags"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITests(TestCase):
    """Test the authorized user tags API"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_rertrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = SerializerTag(tags,many=True)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,serializer.data)

    def test_tag_limited_to_user(self):
        """Test that tags are returned to authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test1@test.com',
            'testpass'

        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user= self.user, name='Comfort food')
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['name'],tag.name)



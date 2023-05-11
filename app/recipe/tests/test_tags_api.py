"""
Tests for the Tags API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
    User,
)

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id) -> str:
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123') -> User:
    """Helper function to create a user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Tests unauthenticated tag API access"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test that authentication is required"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Tests authenticated tag API requests"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user"""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Brazilian')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        payload = {'name': 'Brazilian'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        url = detail_url(tag_id=tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Apples')
        tag2 = Tag.objects.create(user=self.user, name='Turkey')
        tag3 = Tag.objects.create(user=self.user, name='Ginger')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Apple crumble',
            time_minutes=5,
            price=Decimal('10.00'),
        )
        recipe.tags.add(tag1)
        recipe.tags.add(tag2)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertNotIn(tag3, res.data)

    def test_filtered_tags_unique(self):
        """Test that filtered tags are unique."""
        tag = Tag.objects.create(user=self.user, name='Apples')
        Tag.objects.create(user=self.user, name='Turkey')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Apple crumble',
            time_minutes=5,
            price=Decimal('10.00'),
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Apple pie',
            time_minutes=5,
            price=Decimal('10.00'),
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

"""
tests for tag api
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
)
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    # create and return a tag detail url

    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='123456'):
    # create and return a user

    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    # test: unauthenticated api requests

    def setUp(self):
        # simply make an api request
        # from client
        self.client = APIClient()

    def test_auth_required(self):
        # test: auth is required to retrieve tags

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    # test: authenticated api requests

    def setUp(self):
        # force authenticate a user (mock login)
        # and then make an api request from client
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        # test: retrieve the list of tags

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')

        # feeling this might be something similar to
        # JSON.stringify() in JS/TS?
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        # test: retrieved tags belong to the signed in user

        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        # test: update a tag

        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        # test: delete a tag

        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        # test: listing tags to those assigned to recipes

        tag_one = Tag.objects.create(user=self.user, name='Breakfast')
        tag_two = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Avocado toast',
            time_minutes=15,
            price=Decimal('18.99'),
            user=self.user,
        )
        recipe.tags.add(tag_one)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer_one = TagSerializer(tag_one)
        serializer_two = TagSerializer(tag_two)
        self.assertIn(serializer_one.data, res.data)
        self.assertNotIn(serializer_two.data, res.data)

    def test_filtered_tags_unique(self):
        # test: filtered tags returns a unique list

        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe_one = Recipe.objects.create(
            title='Vegan pancake',
            time_minutes=25,
            price=Decimal('5.99'),
            user=self.user
        )
        recipe_two = Recipe.objects.create(
            title='Vegan ramen',
            time_minutes=20,
            price=Decimal('13.99'),
            user=self.user
        )
        recipe_one.tags.add(tag)
        recipe_two.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

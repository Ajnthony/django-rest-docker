"""
tests for ingredients api
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Ingredient,
    Recipe,
)
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    # create and return an ingredient detail url

    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='123456'):
    # create and return a user

    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    # test: unauthenticated api requests

    def setUp(self):
        # there's no self.user = create_user()
        # which means there would be no user object
        # for this testcase
        self.client = APIClient()

    def test_auth_required(self):
        # test: auth is required to retrieve ingredients

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    # test: authenticated api requests

    def setUp(self):
        # self.user here means, for this test,
        # there is a user signed in
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        # test: get the list of ingredients

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Cabbage')

        res = self.client.get(INGREDIENTS_URL)

        # '-name' can be replaced by any field
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        # test: list of ingredients is limited to signed in user

        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Spinach')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        # test: updating an ingredient

        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {
            'name': 'Coriander'
        }

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        # test: delete an ingredient

        ingredient = Ingredient.objects.create(user=self.user, name='lettuce')
        url = detail_url(ingredient.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        # test: listing ingredients by those assigned to recipes

        ingredient_one = Ingredient.objects.create(
            user=self.user, name='Apple')
        ingredient_two = Ingredient.objects.create(
            user=self.user, name='Orange')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=15,
            price=Decimal('4.99'),
            user=self.user
        )
        recipe.ingredients.add(ingredient_one)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer_one = IngredientSerializer(ingredient_one)
        serializer_two = IngredientSerializer(ingredient_two)

        self.assertIn(serializer_one.data, res.data)
        self.assertNotIn(serializer_two.data, res.data)

    def test_filtered_ingredients_unique(self):
        # test: filtered ingredients returns a unique list

        ingredient = Ingredient.objects.create(user=self.user, name='Just Egg')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe_one = Recipe.objects.create(
            title='Vegan egg in hell',
            time_minutes=60,
            price=Decimal('16.99'),
            user=self.user
        )
        recipe_two = Recipe.objects.create(
            title='Vegan egg benedict',
            time_minutes=60,
            price=Decimal('15.99'),
            user=self.user
        )
        recipe_one.ingredients.add(ingredient)
        recipe_two.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

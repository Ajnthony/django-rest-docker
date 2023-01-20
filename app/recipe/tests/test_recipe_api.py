"""
tests for recipe apis
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    # create and return a recipe details url

    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    # create and return a sample recipe

    # all random values
    defaults = {
        'title': 'Sample vegan recipe title',
        'time_minutes': 40,
        'price': Decimal('5.99'),
        'description': 'Sample vegan description',
        'link': 'http://www.wikipedia.com'
    }

    # use values in params, if given,
    # or use default values in the dictionary above
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    # create and return a new user

    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    # test: unauthenticated recipe api requests

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # test: auth is required to make request

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    # test: authenticated api requests

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='123456')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        # test: retrival of the list of recipes

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')

        # data dictionary of the objects
        # which is passed through the serializer
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_list_limited_to_user(self):
        # test: get the list of recipe that belongs to authenticated user

        other_user = create_user(email='other@example.com', password='123456')

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        # test: get recipe detail

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        # test: create a recipe

        payload = {
            'title': 'Sample vegan recipe',
            'time_minutes': 30,
            'price': Decimal('5.99')
        }

        # /api/recipes/recipe
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        # test: partial update of a recipe

        original_link = 'https://www.wikipedia.com'
        recipe = create_recipe(
            user=self.user,
            title='Sample vegan recipe title',
            link=original_link
        )

        payload = {'title': 'Updated vegan recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # again updated value needs to be
        # manually refreshed and updated
        recipe.refresh_from_db()

        # to check if no other fields have been updated
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        # test: full update of recipe

        recipe = create_recipe(
            user=self.user,
            title='Sample vegan recipe title',
            link='http://www.wikipedia.com',
            description='Sample vegan recipe description'
        )

        payload = {
            'title': 'New sample vegan recipe title',
            'link': 'http://www.wikipedia.com/Kale',
            'description': 'New sample vegan recipe description',
            'time_minutes': 10,
            'price': Decimal('2.99')
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        # test: changing recipe.user should return an error

        new_user = create_user(email='test@example.com', password='123456')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        # test: deletion of the recipe

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        # test: trying to delete another user's recipe returns an error

        new_user = create_user(email='user1@example.com', password='123456')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        # test: creating a new recipe with new tags

        payload = {
            'title': 'Vegan Pad See Ew',
            'time_minutes': 20,
            'price': Decimal('14.99'),
            'tags': [{'name': 'Thai'}, {'name': 'a-la-carte'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)

        # the following line makes sure that,
        # during test,
        # a recipe object did get created in the db
        # so that indexing in the next line makes sense
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        # test: creating a new recipe with existing tags

        tag_vegan = Tag.objects.create(user=self.user, name='Vegan')
        payload = {
            'title': 'Hamburger',
            'time_minutes': 10,
            'price': Decimal('9.99'),
            'tags': [{'name': 'Vegan'}, {'name': 'Fast-food'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_vegan, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        # test: creating a tag when updating a recipe

        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'starter'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='starter')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        # test: assigning an existing tag when updating a recipe

        # mock a recipe obj in the db
        # with a tag 'breakfast'
        tag_breakfast = Tag.objects.create(user=self.user, name='breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        # mock an api call
        # with a new tag 'lunch'
        # so basically updating the tag
        tag_lunch = Tag.objects.create(user=self.user, name='lunch')
        payload = {'tags': [{'name': 'lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        # test: clearing all tags from a recipe

        tag_one = Tag.objects.create(user=self.user, name='breakfast')
        tag_two = Tag.objects.create(user=self.user, name='lunch')
        tag_three = Tag.objects.create(user=self.user, name='dinner')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_one)
        recipe.tags.add(tag_two)
        recipe.tags.add(tag_three)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        # test: creating a new recipe with new ingredients

        payload = {
            'title': 'Cauliflower rice',
            'time_minutes': 60,
            'price': Decimal('9.99'),
            'ingredients': [{'name': 'Cauliflower'}, {'name': 'Salt'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        # test: creating a new recipe with existing ingredients

        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        payload = {
            'title': 'Lemon grab',
            'time_minutes': 15,
            'price': Decimal('8.99'),
            'ingredients': [{'name': 'Lemon'}, {'name': 'grab'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ing in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ing['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        # test: creating an ingredient when updating a recipe

        recipe = create_recipe(user=self.user)
        payload = {'ingredients': [{'name': 'Garlic'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Garlic')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        # test: assign an existing ingredient when updating a recipe

        ingredient_one = Ingredient.objects.create(
            user=self.user, name='Oregano')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_one)

        ingredient_two = Ingredient.objects.create(
            user=self.user, name='Rosemary')
        payload = {'ingredients': [{'name': 'Rosemary'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_two, recipe.ingredients.all())
        self.assertNotIn(ingredient_one, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        # test: clearing ingredients from a recipe

        ingredient = Ingredient.objects.create(user=self.user, name='Turmeric')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

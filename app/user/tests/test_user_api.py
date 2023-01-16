"""
tests for user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# url endpoints
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    # create and return a new user
    return get_user_model().objects.create_user(**params)

# public/private
# public: requests that do not require authentication
# private: ones that do


class PublicUserApiTests(TestCase):
    # test public features of the user api
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        # test creating a new user is succssful
        payload = {
            'email': 'test@example.com',
            'password': '123456',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        # test if an error is returned when an email is already in use
        payload = {
            'email': 'test@example.com',
            'password': '123456',
            'name': 'Test Name'
        }

        create_user(**payload)  # just like spread operator in JS/TS
        # how's it different with simply passing in (payload)?
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        # test if an error is returned when len(password) < 5
        payload = {
            'email': 'test@example.com',
            'password': '123',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        # so "assert" means to set the value manually to False
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # test for the generation of token for valid credentials
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': '123456'
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        # test if it returns an error with wrong credentials
        create_user(email='test@example.com', password='123456')

        payload = {'email': 'test@example.com', 'password': '654321'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        # test if posting a blank password returns an error
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        # test authentication is required for users
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    # authenticated tests (signed in)
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='123456',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        # test the retrieval of profile for logged in user
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        # test: /me endpoint is for GET only and no POST
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        # test: update user profile for the logged in user
        payload = {
            'name': 'Updated Name',
            'password': '456123'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # not done automatically
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

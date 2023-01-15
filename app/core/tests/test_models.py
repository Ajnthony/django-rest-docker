"""
tests for models
"""

from django.test import TestCase
# use this to get the reference to custom models
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        # test creating a user with an email is successful
        email = 'test@example.com'
        password = '123456'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        # test if email is normalised for users

        # the custom rule here:
        # domain, or right to @, should always be lowercased
        # the name part, or left to @, could be accepted as entered
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, '123456')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        # test if creating a user without an email raises an error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '123456')

    def test_create_super_user(self):
        # test creating a super user
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            '123456'
        )
        self.assertTrue(user.is_superuser)  # provided by PermissionsMixin
        self.assertTrue(user.is_staff)

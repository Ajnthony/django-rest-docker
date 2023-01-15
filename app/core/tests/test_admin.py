"""
tests for django admin modification
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    # test for django admin

    # not suer why this is not in snake case
    def setUp(self):
        # create a user and client
        self.client = Client()

        # create an admin superuser
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='123456'
        )
        self.client.force_login(self.admin_user)

        # create a regular user
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='123456',
            name='Test user'
        )

    def test_users_list(self):
        # test that users are listed on page
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        # test if edit user page works

        # the url will look like
        # .../core/user/change/{user.id}
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        # test if the create user page works
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

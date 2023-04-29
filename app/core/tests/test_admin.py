""""
Tests for the Django admin modifications.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTests(TestCase):
    """"
    Tests for Django admin.
    """

    def setUp(self: 'AdminSiteTests') -> None:
        """"
        Crete user and client.
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="test123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="test123",
            name="Test user",
        )

    def test_users_listed(self: 'AdminSiteTests') -> None:
        """
        Test that users are listed on user page.
        """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self: 'AdminSiteTests') -> None:
        """
        Test if the edit user page works.
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

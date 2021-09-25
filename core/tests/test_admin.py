from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status


class TestAdmin(TestCase):
    """Test admin site"""

    def setUp(self):
        
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            email = 'test_superuser@gmail.com',
            password = 'testpassword'
        )

        self.client.force_login(self.superuser)

        self.user = get_user_model().objects.create_user(
            email = 'test_user@gmail.com',
            password = 'testpassword'
        )

    def test_users_list(self):
        """Test the user's list on admin url"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test the user's change page"""

        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Test the create user admin page"""

        url = reverse('admin:core_user_add')
        res = self.client.get(url)
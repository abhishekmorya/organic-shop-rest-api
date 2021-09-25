from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create a sample user with params provided"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the public user api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test by creating a valid user"""

        payload = {
            'email': 'test_user@gmail.com',
            'name': 'A name',
            'password': 'testpassword',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(user.email, payload['email'])
        self.assertEqual(user.name, payload['name'])
        self.assertTrue(user.check_password(payload['password']))

    def test_user_exist(self):
        """Test User exist"""

        payload = {
            'email': 'test_user@gmail.com',
            'name': 'A name',
            'password': 'testpassword'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test the password max length"""

        payload = {
            'email': 'test_user@gmail.com',
            'name': 'A name',
            'password': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # double check if user not created
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test creating token for a valid user"""

        payload = {
            'email': 'test_user@gmail.com',
            'password': 'testpassword'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_creating_token_invalid_credentials(self):
        """Test creating token for invalid user credentials"""
        payload = {
            'email': 'test_user@gmail.com',
            'name': 'A name',
            'password': 'testpassword'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, {
                'email': 'test_user@gmail.com',
                'password': 'password'
            })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_creating_token_no_user(self):
        """Test creating token for user which doesn't exist"""
        paylaod = {
            'email': 'test_user@gmail.com',
            'password': 'testpassword',
        }

        res = self.client.post(TOKEN_URL, paylaod)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """Test creating token for missing email or passsword"""

        res = self.client.post(TOKEN_URL, 
            {
                'email': 'test_user@gmail.com', 
                'passorrd': 'password'
            }
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_unauthenticated_user(self):
        """Test that authentication is required"""
        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test api requests which needs authentication"""

    def setUp(self):
        self.client = APIClient()

        payload = {
            'email': 'test_user@gmail.com',
            'password': 'testpassword'
        }
        self.user = create_user(**payload)

        self.client.force_authenticate(user = self.user)

    def test_retrieve_profile_access(self):
        """Test retrieving profile for logged in user"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_to_me_not_allowed(self):
        """Test that post request not allowed on me url"""
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update profile for logged in user"""
        payload = {
            'name':'New Name',
            'password': 'newpassword'
        }        

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(payload['name'], self.user.name)
        self.assertTrue(self.user.check_password(payload['password']))
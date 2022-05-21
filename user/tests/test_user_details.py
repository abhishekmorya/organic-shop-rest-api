from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from core.tests.test_models import sample_user
from user import serializers

USER_DETAILS_URL = reverse('user:user-details-list')

def sample_address(user, **params):
    """Create and return a sample address object"""
    defaults = {
        "name": "Abhishek",
        "line1": "Line1",
        "line2": "Line2",
        "city": "Pune",
        "district": "Pune",
        "state": "Maharastra",
        "pincode": "123456",
        "addressType": models.UserAddress.HOME
    }
    defaults.update(params)
    return models.UserAddress.objects.create(user = user, **defaults)

def sample_user_details(user, address):
    """Create and return UserDetails object and return"""
    return models.UserDetails.objects.create(
        user = user, selectedAddress = address)


class TestPublicUserDetails(TestCase):
    """Test the UserDetails api for unauthenticated user"""
    def setUp(self):
        """Initial setup for tests"""
        self.client = APIClient()

    def test_retrieve_details_invalid(self):
        """Test retrieving user details for unauthenticated user is invalid"""
        res = self.client.get(USER_DETAILS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_user_details_invalid(self):
        """Test post request for unauthenticated user"""
        payload = {
            'user': 1,
            'address': 1
        }
        res = self.client.post(USER_DETAILS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateUserDetails(TestCase):
    """Test the UserDetails object for logged in user"""

    def setUp(self):
        """Initial setup for tests"""
        self.client = APIClient()
        self.user = sample_user(
            email = 'test_user@gmail.com',
            password = 'testpassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_user_details(self):
        """Test retrieving UserDetails for logged in user"""
        address1 = sample_address(user = self.user)
        sample_user_details(user = self.user, address = address1)

        res = self.client.get(USER_DETAILS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user_details = models.UserDetails.objects.all()
        serializer = serializers.UserDetailsSerializer(user_details, many = True)

        self.assertEqual(res.data, serializer.data)


    def test_post_user_details(self):
        """Test posting user details"""
        address = sample_address(user = self.user)
        payload = {
            'selectedAddress': address.id
        }
        res = self.client.post(USER_DETAILS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user_detail = models.UserDetails.objects.get(selectedAddress = res.data['selectedAddress'])

        self.assertEqual(res.data['selectedAddress'], user_detail.selectedAddress.id)
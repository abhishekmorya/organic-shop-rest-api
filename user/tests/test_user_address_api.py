from user.serializers import UserAddressSerializer
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import serializers, status
from rest_framework.test import APIClient

from core.models import UserAddress

ADDRESS_URL = reverse('user:address-list')

def detail_url(address_id):
    """Return the detail url for user address"""
    return reverse('user:address-detail', args=[address_id])

def create_user(**params):
    """Create a sample user with params provided"""
    return get_user_model().objects.create_user(**params)

def sample_address(user, **params):
    """Create a sample address for a user"""
    defaults = {
        "name": "Name",
        "line1": "Line1",
        "line2": "Line2",
        "city": "City Name",
        "district": "Disctict Name",
        "state": "State",
        "pincode": "123456",
        "addressType": 1
    }
    defaults.update(params)
    return UserAddress.objects.create(user = user, **defaults)


class PublicUserAddressTests(TestCase):
    """Test cases for user address api for unathenticated user"""
    def setUp(self):
        self.client = APIClient()

    def test_get_address_authentication_required(self):
        """Test that user login is required for getting the address"""
        res = self.client.get(ADDRESS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserAddressTests(TestCase):
    """Test the user address api"""

    def setUp(self):
        self.user = create_user(
            email = 'test_user@gmail.com',
            password = 'testpassword'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_retrieve_addresses(self):
        """Test retrieving address for the logged in user"""
        
        sample_address(self.user)
        sample_address(self.user)

        res = self.client.get(ADDRESS_URL)
        addresses = UserAddress.objects.all()
        serializer = UserAddressSerializer(addresses, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_addresses_limited_to_user(self):
        """Test retrieve addresses limited to logged in user"""

        user2 = create_user(
            email = 'abhishek@gmail.com',
            password = 'testpassword'
        )
        sample_address(user = user2)
        sample_address(user = self.user)

        res = self.client.get(ADDRESS_URL)
        addresses = UserAddress.objects.all().filter(user = self.user)
        serializer = UserAddressSerializer(addresses, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_detailed_address(self):
        """Test retrieve detail of single address"""
        address = sample_address(user = self.user)
        url = detail_url(address.id)
        res = self.client.get(url)

        serializer = UserAddressSerializer(address)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creating_address(self):
        """Test creating a basic address"""
        payload = {
            'name': 'Abhishek',
            'line1': 'House Number',
            'line2': 'Locality',
            'city': 'City/Town Name',
            'district': 'Your District',
            'state': 'State',
            'pincode': '123456',
            'addressType': 1
        }
        res = self.client.post(ADDRESS_URL, payload)
        # print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        address = UserAddress.objects.get(id = res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(address, key))
    
    def test_delete_address(self):
        """Test deleting a address"""
        payload = {
            'name': 'Abhishek',
            'line1': 'House Number',
            'line2': 'Locality',
            'city': 'City/Town Name',
            'district': 'Your District',
            'state': 'State',
            'pincode': '123456',
            'addressType': 1
        }
        sample_address(user = self.user)
        address1 = sample_address(user=self.user, **payload)
        url = detail_url(address1.id)
        res = self.client.delete(url)
        # self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        addresses = UserAddress.objects.all()
        serializer = UserAddressSerializer(addresses, many = True)
        self.assertEqual(len(serializer.data), 1)
    
    def test_partial_update_address(self):
        """Test updating address partialy with patch"""
        address = sample_address(user = self.user)
        url = detail_url(address_id = address.id)

        payload = {
            'name': 'Abhishek',
            'city': 'Yamunanagar'
        }
        res = self.client.patch(url, payload)
        address.refresh_from_db()
        # self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(address.name, payload['name'])
        self.assertEqual(address.city, payload['city'])

    def test_full_update_address(self):
        """Test updating address fully with put method"""

        address = sample_address(user = self.user)
        url = detail_url(address_id = address.id)

        payload = {
            'name': 'Abhishek',
            'line1': 'House Number',
            'line2': 'Locality',
            'city': 'City/Town Name',
            'district': 'Your District',
            'state': 'State',
            'pincode': '123456',
            'addressType': 1
        }
        res = self.client.put(url, payload)
        address.refresh_from_db()

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(address, key))
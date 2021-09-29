from product.tests.test_category_api import sample_category
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import utils
from django.core.exceptions import ValidationError

from core import models


def sample_user(email='test_user@gmail.com', password='testpassword', is_staff = True):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        is_staff=is_staff
    )


class ModelTest(TestCase):
    """Test class for models"""

    def test_create_user_with_email_successful(self):
        """Test creating user with new email"""

        email = "abhishek@gmail.com"
        password = 'testpassword'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_with_email_normalize(self):
        """Test the new user created with email normalized"""

        email = "abhishek@GMAIL.COM"
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_mail(self):
        """Test creating user with no email raise Value error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='Testpassword'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        email = 'abhishek@gmail.com'
        password = 'testpassword'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_address_str(self):
        """Test the address string representation"""
        user = sample_user()

        payload = {
            "name": "Name",
            "line1": "Line1",
            "line2": "Line2",
            "city": "City Name",
            "district": "Disctict Name",
            "state": "State",
            "pincode": "123456",
            "addressType": models.UserAddress.HOME
        }
        address = models.UserAddress.objects.create(user = user, **payload)

        self.assertEqual(str(address), 
            'name: {}, district: {}, state: {}, pincode: {}'.format(
                address.name,
                address.district,
                address.state,
                address.pincode
            )
        )
    
    def test_category_str(self):
        """Test the string representation of category object"""
        user = sample_user()
        payload = {
            'name': 'Category',
            'desc': "Category desc"
        }

        category = models.Category.objects.create(user = user, **payload)
        self.assertEqual(str(category), payload['name'])

    def test_unique_categories(self):
        """Test no duplicate categories are created"""
        user = sample_user()
        models.Category.objects.create(user = user, name = 'Category')
        # models.Category.objects.create(user = user, name = 'Category')

        with self.assertRaises(utils.IntegrityError):
            models.Category.objects.create(user = user, name = 'Category')

    def test_product_str(self):
        """Test the string representation of product object"""

        user = sample_user()
        category = sample_category(user = user)
        payload = {
            'category': category,
            'title': 'Brown Bread',
            'desc': 'Healthy Brown bread',
            'price': 23.00,
            'quantity': 5,
            'unit': models.Product.UNIT,
            'image': 'image url'
        }

        product = models.Product.objects.create(user = user, **payload)

        self.assertEqual(str(product), payload['title'])
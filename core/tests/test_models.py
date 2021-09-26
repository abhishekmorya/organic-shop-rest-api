from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test_user@gmail.com', password='testpassword'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        is_staff=True
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
            "addressType": 1
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

from django.utils import timezone
from datetime import datetime
from product.tests.test_category_api import sample_category
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import utils

from unittest.mock import patch

from core import models


def sample_user(email='test_user@gmail.com', password='testpassword', is_staff = True):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        is_staff=is_staff
    )


def sample_address(user, **params):
    """Create and return a sample address object"""
    defaults = {
        "name": "Name",
        "line1": "Line1",
        "line2": "Line2",
        "city": "City Name",
        "district": "Disctict Name",
        "state": "State",
        "pincode": "123456",
        "addressType": models.UserAddress.HOME
    }
    defaults.update(params)
    return models.UserAddress.objects.create(user = user, **defaults)


def sample_category(user, **params):
    """Create and return a sample category object"""
    defaults = {
        'name': "Fruits",
        'desc': 'Fresh Fruits'
    }
    defaults.update(params)
    return models.Category.objects.create(user = user, **defaults)


def sample_product(user, **params):
    """Create and return a sample product object"""
    category = params['category'] if 'category' in params.keys() else sample_category(user)
    defaults = {
        'category': category,
        'title': 'Brown Bread',
        'desc': 'Healthy Brown bread',
        'price': 23.00,
        'quantity': 5,
        'unit': models.Product.UNIT,
        'image': 'image url'
    }
    defaults.update(params)
    return models.Product.objects.create(user = user, **defaults)


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

    @patch('uuid.uuid4')
    def test_product_filename_uuid(self, mock_uuid):
        """Test product image is saved to correct path"""

        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.uploaded_images_for_products(None, 'my-image.jpg')
        exp_path = f'uploads/products/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    def test_one_to_one_mapping_of_user_address(self):
        """Test the one to one mapping of user and UserAddress"""
        user = sample_user()
        address1 = sample_address(user = user)
        payload = {
            "name": "Abhishek",
            "line1": "Line1",
            "line2": "Line2",
            "city": "Pune",
            "district": "Pune",
            "state": "Maharastra",
            "pincode": "123456",
            "addressType": models.UserAddress.HOME
        }
        address2 = sample_address(user = user, **payload)

        user_details = models.UserDetails.objects.create(
                        user = user, selectedAddress = address1)

        user_details.selectedAddress = address2

        self.assertEqual(str(user_details.selectedAddress), str(address2))

    def test_shopping_cart_str(self):
        """Test string representation of Shopping Cart Object"""
        user = sample_user()
        product = sample_product(user)

        payload = {
            'product': product,
            'count': 2
        }
        shoppingCart = models.ShoppingCart.objects.create(user = user, **payload)
        count = models.ShoppingCart.objects.count()
        self.assertEqual(f"{str(product)}, {payload['count']}", str(shoppingCart))
        

    def test_payment_mode_str(self):
        """Test string representation of Payment mode object"""
        payload = {
            'title': 'UPI',
            'desc': 'UPI payment',
            'charges': 2.2,
            'enabled': True
        }
        paymentMode = models.PaymentMode.objects.create(**payload)
        self.assertEqual(payload['title'], str(paymentMode))

    def test_offer_str(self):
        """Test string representation of Offer object"""
        user = sample_user()
        payload = {
            'title': 'Summer Season', 
            'percentage': 20.5,
            'desc': 'Summer season sale of 2022',
            'expiry_date': timezone.make_aware(datetime(2022, 6, 30, 23,59,59))
        }

        offer = models.Offer.objects.create(user = user, **payload)
        self.assertEqual(payload['title'], str(offer))

    def test_creating_order(self):
        """Test string representation of Order"""
        user = sample_user()
        address = sample_address(user)
        payment_mode = models.PaymentMode.objects.create(
            **{
                'title': 'UPI',
                'desc': 'UPI payment',
                'charges': 2.2,
                'enabled': True
            }
        )

        payload = {
            'shipping_address': address,
            'billing_address': address,
            'payment_mode': payment_mode
        }
        order = models.Order.objects.create(user = user, **payload)

        product1 = sample_product(user)
        sc1 = models.ShoppingCart.objects.create(user = user, product = product1, count = 4)
        product_payload = {
            'category': sample_category(user, name = 'Sauce'),
            'title': 'Jam',
            'desc': 'The sweet sour Jam',
            'price': 10.00,
            'quantity': 2,
            'unit': models.Product.UNIT,
            'image': 'image url'
        }
        product2 = sample_product(user, **product_payload)
        sc2 = models.ShoppingCart.objects.create(user = user, product = product2, count = 3)
        order.cartItems.add(sc1, sc2)
        offer = models.Offer.objects.create(
            user = user,
            title = 'Summer Sale',
            percentage = 20.5,
            desc = 'Summer Sale 2022',
            expiry_date = timezone.make_aware(datetime(2022, 6, 30, 23, 59, 59))
        )
        order.offers_applied.add(offer)
        count = models.Order.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(order.cartItems.count(), 2)
        self.assertEqual(order.offers_applied.count(), 1)

    def test_creating_price_detail(self):
        """Test creating price details"""
        user = sample_user()
        address = sample_address(user)
        payment_mode = models.PaymentMode.objects.create(
            **{
                'title': 'UPI',
                'desc': 'UPI payment',
                'charges': 2.2,
                'enabled': True
            }
        )

        order_payload = {
            'shipping_address': address,
            'billing_address': address,
            'payment_mode': payment_mode
        }
        order = models.Order.objects.create(user = user, **order_payload)
        product1 = sample_product(user)
        sc1 = models.ShoppingCart.objects.create(user = user, product = product1, count = 4)
        product_payload = {
            'category': sample_category(user, name = 'Sauce'),
            'title': 'Jam',
            'desc': 'The sweet sour Jam',
            'price': 10.00,
            'quantity': 2,
            'unit': models.Product.UNIT,
            'image': 'image url'
        }
        product2 = sample_product(user, **product_payload)
        sc2 = models.ShoppingCart.objects.create(user = user, product = product2, count = 3)
        order.cartItems.add(sc1, sc2)
        offer = models.Offer.objects.create(
            user = user,
            title = 'Summer Sale',
            percentage = 20.5,
            desc = 'Summer Sale 2022',
            expiry_date = timezone.make_aware(datetime(2022, 6, 30, 23, 59, 59))
        )
        order.offers_applied.add(offer)
        payload = {
            'order': order,
            'delievery_charges': 50.5
        }
        
        models.PriceDetail.objects.create(user = user, **payload)
        self.assertEqual(1, models.PriceDetail.objects.count())
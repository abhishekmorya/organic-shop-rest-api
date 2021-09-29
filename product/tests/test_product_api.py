import product
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Category
from product.serializers import ProductSerializer

PRODUCT_URL = reverse('product:product-list')


def detail_url(product_id):
    """Returns the details url for product"""
    return reverse('product:product-detail', args=[product_id])


def sample_user(email='test_user@gmail.com', password='testpassword', is_staff=True):
    """Create and return admin user"""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        is_staff=is_staff
    )


def sample_category(user, **params):
    """Create sample category and return"""
    defaults = {
        'name': 'Bread',
        'desc': 'Bread desc',
    }
    defaults.update(params)
    return Category.objects.create(user=user, **defaults)


def sample_product(user, category, **params):
    """Create sample product and return"""
    defaults = {
        'category': category,
        'title': 'Brown Bread',
        'desc': 'Healthy Brown bread',
        'price': 23.00,
        'quantity': 5,
        'unit': Product.UNIT,
    }
    defaults.update(params)
    return Product.objects.create(user=user, **defaults)


class TestPublicProductApi(TestCase):
    """Test the product api for unauthenticated user"""

    def setUp(self):
        """Initial set up for test cases"""
        self.client = APIClient()

    def test_retrieving_product_successful(self):
        """Test retrieving products for unauthenticated user"""
        res = self.client.get(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthorized_post_invalid(self):
        """Test that unauthorized user not allowed to create product"""
        user = sample_user(
            email='test_user2@gmail.com',
            is_staff=False
        )
        user_admin = sample_user()
        category = sample_category(user=user_admin)
        self.client.force_login(user)

        payload = {
            'category': category,
            'title': 'Brown Bread',
            'desc': 'Healthy Brown bread',
            'price': 23.00,
            'quantity': 5,
            'unit': Product.UNIT,
        }

        res = self.client.post(PRODUCT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateProductApi(TestCase):
    """Test product api for logged in users"""

    def setUp(self):
        """Initial setup for tests"""
        self.client = APIClient()
        self.user = sample_user(
            email='test_user@gmail.com',
            password='testpassword',
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_products(self):
        """Test retrieving products for a logged in user"""
        category = sample_category(user=self.user)
        sample_product(user=self.user, category=category)
        sample_product(user=self.user, category=category)
        res = self.client.get(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_post_product_by_admin_successful(self):
        """Test creating products by admin user"""
        category = sample_category(user=self.user)
        payload = {
            "title": "Banana",
            "desc": "Banana desc",
            "category": category.id,
            "price": 20.00,
            "quantity": 12,
            "unit": 0
        }
        res = self.client.post(PRODUCT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        serializer = ProductSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_by_admin_successful(self):
        """Test the partial upate by patch action"""
        category = sample_category(user=self.user)
        category2 = sample_category(user=self.user, name='Fruit')
        product = sample_product(user=self.user, category=category)

        payload = {
            'title': 'Apple',
            'category': category2.id,
            'price': 100.00,
        }

        url = detail_url(product_id=product.id)
        self.client.patch(url, payload)
        product.refresh_from_db()

        self.assertEqual(payload['title'], product.title)
        self.assertEqual(payload['price'], product.price)
        self.assertEqual(payload['category'], category2.id)

    def test_full_update_by_admin_successful(self):
        """Test the full update by put action"""
        category = sample_category(user=self.user)
        product = sample_product(user=self.user, category=category)
        url = detail_url(product_id=product.id)
        payload = {
            "title": "Banana",
            "desc": "Banana desc",
            "category": category.id,
            "price": 20.00,
            "quantity": 12,
            "unit": 0
        }
        self.client.put(url, payload)
        product.refresh_from_db()

        for key in payload:
            if key != 'category':
                self.assertEqual(payload[key], getattr(product, key))
        self.assertEqual(payload['category'], product.category.id)

    def test_delete_by_admin_successful(self):
        """Test the delete action by admin"""
        category = sample_category(user=self.user)
        payload = {
            "title": "Banana",
            "desc": "Banana desc",
            "category": category.id,
            "price": 20.00,
            "quantity": 12,
            "unit": 0
        }
        product1 = sample_product(user=self.user, category=category)
        pid = product1.id
        url = detail_url(product_id=pid)

        self.client.delete(url)
        products = Product.objects.filter(id=pid)
        self.assertEqual(len(products), 0)

    def test_filter_products_with_category(self):
        """Test filtering the products with category"""
        category1 = sample_category(user=self.user, name='Cat 1')
        category2 = sample_category(user=self.user, name='Cat 2')
        category3 = sample_category(user=self.user, name='Cat 3')
        product1 = sample_product(user=self.user, category=category1)
        product2 = sample_product(user=self.user, category=category2, title='Product2',
                                  desc='Product2', price=20.00, quantity=2, unit=Product.KG)
        product3 = sample_product(user=self.user, category=category3, title='Product3',
                                  desc='Product3', price=10.00, quantity=5, unit=Product.LTR)

        res = self.client.get(PRODUCT_URL, {
            'categories': f'{category1.id}, {category2.id}'
        })
        
        products = Product.objects.filter(category__in = [category1.id, category2.id])
        serializer = ProductSerializer(products, many = True)
        self.assertEqual(res.data, serializer.data)
        self.assertNotIn(product3, res.data)
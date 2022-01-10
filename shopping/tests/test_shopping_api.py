from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from shopping.serializers import ShoppingDetailSerializer, ShoppingSerializer

SHOPPING_URL = reverse('shopping:shopping-list')

def detail_url(shopping_id):
    """Returns the detailed url for shopping cart"""
    return reverse('shopping:shopping-detail', args=[shopping_id])

def sample_user(email = 'testuser@gmail.com', password = 'testuser', is_staff = True):
    """Create sample user"""
    return get_user_model().objects.create(
        email = email,
        password = password,
        is_staff = is_staff
    )

def sample_category(user, **params):
    """Create sample Category"""
    defaults = {
        'name': 'Bread',
        'desc': 'Bread desc',
    }
    defaults.update(params)
    return models.Category.objects.create(user=user, **defaults)

def sample_product(user, category, **params):
    """Create product object"""
    defaults = {
        'category': category,
        'title': 'Brown Bread',
        'desc': 'Healthy Brown bread',
        'price': 23.00,
        'quantity': 5,
        'unit': models.Product.UNIT,
    }
    defaults.update(params)
    return models.Product.objects.create(user=user, **defaults)

def sample_shopping_item(user, product, count = 2):
    """Create sample cart Item with provided values"""
    payload = {
        'product': product,
        'count': count
    }
    return models.ShoppingCart.objects.create(user = user, **payload)


class TestPublicShoppingAPI(TestCase):
    """Test the shopping cart api for unauthorized users"""

    def setUp(self):
        """Set Up attributes for Testing"""
        self.client = APIClient()

    def test_retrieving_shopping_cart(self):
        """Test the fetching cart details for unauthorised user"""
        res = self.client.get(SHOPPING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_post(self):
        """Test the post request from unauthorised user"""
        user = sample_user()
        category = sample_category(user)
        payload = {
            'product': sample_product(user, category),
            'count': 2
        }
        res = self.client.post(SHOPPING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateShoppingCartApi(TestCase):
    """Test the public API of Shopping Cart"""

    def setUp(self):
        """Set up for Private testing"""
        self.client = APIClient()
        self.user = sample_user(is_staff=False)
        self.category = sample_category(self.user)
        self.product = sample_product(self.user, self.category)
        self.client.force_authenticate(self.user)

    def test_list_shopping_cart(self):
        """Test fetching the shopping cart with logged in user"""
        sample_shopping_item(self.user, self.product)
        product2 = sample_product(self.user, self.category, title = 'Mango')
        sample_shopping_item(self.user, product2)
        res = self.client.get(SHOPPING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cart_items = models.ShoppingCart.objects.all().order_by('id')
        serializer = ShoppingSerializer(cart_items, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_shopping_list_limited_to_user(self):
        """Test that shopping list are viewed only by same user"""
        sample_shopping_item(self.user, self.product)
        user2 = sample_user(
            email='new_user@gmail.com',
            password='testpassword',
            is_staff=False
        )
        sample_shopping_item(user2, self.product)
        res = self.client.get(SHOPPING_URL)
        cart_items = models.ShoppingCart.objects.all().filter(user = self.user)
        serializer = ShoppingSerializer(cart_items, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_shopping_retrieve_detail(self):
        """Test the detailed shopping item"""
        cart_item = sample_shopping_item(self.user, self.product)
        url = detail_url(shopping_id = cart_item.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = ShoppingDetailSerializer(cart_item)
        self.assertEqual(res.data, serializer.data)

    def test_create_shopping_cart(self):
        """Test the creation of cart item"""
        payload = {
            'product': self.product.id,
            'count': 3
        }
        res = self.client.post(SHOPPING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cart_item = models.ShoppingCart.objects.get(id = res.data['id'])
        serializer = ShoppingSerializer(cart_item)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_shopping_cart(self):
        """Test the partial update to shopping cart (count)"""
        cartItem = sample_shopping_item(self.user, self.product, count = 1)
        payload = {
            'count': 3
        }
        url = detail_url(shopping_id = cartItem.id)
        self.client.patch(url, payload)
        cartItem.refresh_from_db()
        self.assertEqual(payload['count'], cartItem.count)

    def test_delete_shopping_cart(self):
        """Test deleting cart Item"""
        sample_shopping_item(self.user, self.product)
        product2 = sample_product(self.user, self.category, title = 'Product2')
        cartItem2 = sample_shopping_item(self.user, product2, count = 5)
        url = detail_url(shopping_id=cartItem2.id)

        self.client.delete(url)
        items = models.ShoppingCart.objects.filter(id = cartItem2.id)
        self.assertEqual(len(items), 0)

    
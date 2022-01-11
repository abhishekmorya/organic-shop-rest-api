from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from shopping import serializers
from shopping.serializers import SessionShoppingSerializer, ShoppingDetailSerializer, ShoppingSerializer

SHOPPING_URL = reverse('shopping:shopping-list')
SESSION_SHOPPING_URL = reverse('shopping:aUser-list')

def detail_url(shopping_id):
    """Returns the detailed url for shopping cart"""
    return reverse('shopping:shopping-detail', args=[shopping_id])

def detail_url_session(shopping_id):
    """Returns the detailed url for shopping session cart"""
    return reverse('shopping:aUser-detail', args=[shopping_id])

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

def sample_shopping_session_item(session_key, product, count = 2):
    """Create sample cart item for anonymous user"""
    payload = {
        'product': product,
        'count': count
    }
    return models.SessionShoppingCart.objects.create(aUser = session_key, **payload)


class TestPublicShoppingAPI(TestCase):
    """Test the shopping cart api for unauthorized users"""

    def setUp(self):
        """Set Up attributes for Testing"""
        self.client = APIClient()
        self.session_key = self.client.session.session_key
        self.user = sample_user()
        self.category = sample_category(self.user)
        self.product = sample_product(self.user, self.category)

    def test_retrieving_shopping_cart(self):
        """Test the fetching cart details for unauthorised user"""
        res = self.client.get(SHOPPING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_post(self):
        """Test the post request from unauthorised user"""
        payload = {
            'product': sample_product(self.user, self.category),
            'count': 2
        }
        res = self.client.post(SHOPPING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_shopping_cart_from_session(self):
        """Test shopping cart retrieving for not logged in user from session"""
        sample_shopping_session_item(self.session_key, self.product)
        res = self.client.get(SESSION_SHOPPING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cartItems = models.SessionShoppingCart.objects.all().order_by('id')
        serializer = SessionShoppingSerializer(cartItems, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_shopping_cart_for_same_session(self):
        """Test shopping cart for multiple sessions"""
        session = self.client.session
        sample_shopping_session_item(self.session_key, self.product)
        session.create()
        session_key2 = session.session_key
        product2 = sample_product(self.user, self.category, title = 'Product2')
        sample_shopping_session_item(session_key2, product2, count  = 1)

        res = self.client.get(SESSION_SHOPPING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cartItems = models.SessionShoppingCart.objects.filter(aUser = self.session_key)
        serializer = serializers.SessionShoppingSerializer(cartItems, many = True)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_shopping_session_retrieve_detail_data(self):
        """Test retrieve detailed data of session shopping cart"""
        item = sample_shopping_session_item(self.session_key, self.product)
        url = detail_url_session(shopping_id = item.id)
        res = self.client.get(url)
        cartItem = models.SessionShoppingCart.objects.get(id = item.id)
        serializer = serializers.SessionShoppingDetailSerializer(cartItem)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_shopping_session_cart_item(self):
        """Test creating session shopping cart item"""
        payload = {
            'product': self.product.id,
            'count': 2
        }
        res = self.client.post(SESSION_SHOPPING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        item = models.SessionShoppingCart.objects.get(id = res.data['id'])
        serializer = serializers.SessionShoppingSerializer(item)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_session_shopping_cart(self):
        """Test partial update session shopping cart for count"""
        item = sample_shopping_session_item(self.session_key, self.product)
        payload = {
            'count': 3
        }
        url = detail_url_session(shopping_id=item.id)
        self.client.patch(url, payload)
        item.refresh_from_db()
        self.assertEqual(payload['count'], item.count)
        
    def test_deleting_session_shopping_cart(self):
        """Test deleting session shopping cart"""
        sample_shopping_session_item(self.session_key, self.product)
        product2 = sample_product(self.user, self.category, title = 'Product 2')
        item2 = sample_shopping_session_item(self.session_key, product2)
        url = detail_url_session(shopping_id=item2.id)
        self.client.delete(url)
        items = models.SessionShoppingCart.objects.all().filter(id = item2.id)
        self.assertEqual(len(items), 0)


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

    
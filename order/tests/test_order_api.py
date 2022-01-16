from django.test.testcases import TestCase
from django.urls.base import reverse
from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth import get_user_model
from django.utils import timezone

from datetime import datetime

from core import models
from order.serializers import OrderDetailSerializer, OrderSerializer
from user.serializers import UserAddressSerializer


ORDER_URL = reverse('order:order-list')

def detail_url(order_id):
    """Return detail url for offer"""
    return reverse('order:order-detail', args=[order_id])


def sample_user(email='testuser@gmail.com', password='testpassword', is_staff=True):
    """Create and returns new user"""
    return get_user_model().objects.create(email=email, password=password, is_staff=is_staff)


def sample_offer(user, **params):
    """Create and returns sample offer"""
    defaults = {
        'title': 'Summer Offer',
        'percentage': 15.0,
        'desc': 'Summer Offer 2021',
        'expiry_date': timezone.make_aware(datetime(2022, 6, 30))
    }
    defaults.update(params)
    return models.Offer.objects.create(user=user, **defaults)


def sample_payment_mode(user, **params):
    """Create and return sample payment mode"""
    defaults = {
        'title': 'UPI Mode',
        'desc': 'UPI payment mode',
        'charges': 0,
        'enabled': True,
    }
    defaults.update(params)
    return models.PaymentMode.objects.create(user=user, **defaults)


def sample_shipping_address(user, **params):
    """Create and return sample address"""
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
    return models.UserAddress.objects.create(user=user, **defaults)


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


def sample_shopping_item(user, product, count=2):
    """Create sample cart Item with provided values"""
    payload = {
        'product': product,
        'count': count
    }
    return models.ShoppingCart.objects.create(user=user, **payload)


def sample_order(user, shipping_address, billing_address, payment_mode):
    """Create and return sample order"""
    return models.Order.objects.create(user=user,
                                       shipping_address=shipping_address.printable(),
                                       billing_address=billing_address.printable(),
                                       payment_mode=payment_mode)


class TestPublicOrderApi(TestCase):
    """Test cases of Order api for anonymous user"""

    def setUp(self):
        """Set Up for Test cases"""
        self.client = APIClient()

    def test_retrieve_order_unauthenticated(self):
        """Test retrieving order for unauthenticated user"""
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_order_unauthenticated(self):
        """Test post order for unauthenticated user"""
        user = sample_user()
        address = sample_shipping_address(user)
        pmode = sample_payment_mode(user)
        payload = {
            'shipping_address': address,
            'billing_address': address,
            'payment_mode': pmode
        }
        res = self.client.post(ORDER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestNormalUserOrderApi(TestCase):
    """Test cases of order for normal user"""

    def setUp(self):
        """Set up for test cases"""
        self.client = APIClient()
        self.user = sample_user(is_staff=False)
        self.client.force_authenticate(self.user)
        self.address = sample_shipping_address(self.user)
        self.payment_mode = sample_payment_mode(self.user, title = 'Internet banking')

    def test_retrieve_orders_normal_user(self):
        """Test retrieve orders for normal user"""
        address = sample_shipping_address(self.user)
        pmode = sample_payment_mode(self.user)
        order = sample_order(self.user, address, address, pmode)
        product = sample_product(self.user, sample_category(self.user))
        order.cartItems.add(sample_shopping_item(self.user, product))
        order.offers_applied.add(sample_offer(self.user))
        res = self.client.get(ORDER_URL)
        orders = models.Order.objects.all().order_by('-id')
        serializer = OrderSerializer(orders, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_post_basic_order_normal_user(self):
        """Test post order normal user"""
        address = sample_shipping_address(self.user)
        pmode = sample_payment_mode(self.user)
        payload = {
            'shipping_address': address.printable(),
            'billing_address': address.printable(),
            'payment_mode': pmode.id,
        }
        res = self.client.post(ORDER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = models.Order.objects.get(id = res.data['id'])
        serializer = OrderSerializer(order)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_order_limited_to_user_order_normal_user(self):
        """Test retrieve order limited to logged in user for normal user"""
        address = sample_shipping_address(self.user)
        pmode = sample_payment_mode(self.user)
        sample_order(self.user, address, address, pmode)
        user2 = sample_user(email='newuser@gmail.com', password='testpass', is_staff=False)
        sample_order(user2, address, address, pmode)
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        orders = models.Order.objects.all().filter(user = self.user)
        serializer = OrderSerializer(orders, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_post_order_with_cartitems_normal_user(self):
        """Test post order adding cart items for normal user"""
        category = sample_category(self.user)
        product1 = sample_product(self.user, category)
        product2 = sample_product(self.user, category, title = 'Product2')
        item1 = sample_shopping_item(self.user, product1)
        item2 = sample_shopping_item(self.user, product2)

        payload = {
            'cartItems': [item1.id, item2.id],
            'shipping_address': self.address.printable(),
            'billing_address': self.address.printable(),
            'payment_mode': self.payment_mode.id,
        }
        res = self.client.post(ORDER_URL, payload)
        order = models.Order.objects.get(id = res.data['id'])
        items = order.cartItems.all()
        self.assertEqual(len(items), 2)
        self.assertIn(item1, items)
        self.assertIn(item2, items)

    def test_post_order_with_offers_normal_order(self):
        """Test post order with offers for normal user"""
        offer1 = sample_offer(self.user)
        offer2 = sample_offer(self.user, title = 'Winter offer')
        payload = {
            'offers_applied': [offer1.id, offer2.id],
            'shipping_address': self.address.printable(),
            'billing_address': self.address.printable(),
            'payment_mode': self.payment_mode.id,
        }
        res = self.client.post(ORDER_URL, payload)
        order = models.Order.objects.get(id = res.data['id'])
        offers = order.offers_applied.all()
        self.assertEqual(len(offers), 2)
        self.assertIn(offer1, offers)
        self.assertIn(offer2, offers)

    def test_retrieve_detail_order_normal_user(self):
        """Test retrieve detail order for normal user"""
        order = sample_order(self.user, self.address, self.address, self.payment_mode)
        product = sample_product(self.user, sample_category(self.user))
        item = sample_shopping_item(self.user, product)
        offer = sample_offer(self.user)
        order.cartItems.add(item)
        order.offers_applied.add(offer)
        url = detail_url(order.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = OrderDetailSerializer(order)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_order_normal_user(self):
        """Test partial update order"""
        order = sample_order(self.user, self.address, self.address, self.payment_mode)
        address2 = sample_shipping_address(self.user, name = 'Address 2')
        payment_mode = sample_payment_mode(self.user, title = 'Credit Card')
        offer = sample_offer(self.user)
        order.offers_applied.add(offer)
        offer2 = sample_offer(self.user, title = 'Winter Offer 2022')

        payload = {
            'offers_applied': [offer2.id,],
            'billing_address': address2.printable(),
            'payment_mode': payment_mode.id
        }
        url = detail_url(order.id)
        self.client.patch(url, payload)
        order.refresh_from_db()
        offers = order.offers_applied.all()
        self.assertIn(offer2, offers)
        self.assertEqual(payload['billing_address'], order.billing_address)
        self.assertEqual(payload['payment_mode'], order.payment_mode.id)

    def test_full_update_order_normal_user(self):
        """Test full update order for normal user"""
        order = sample_order(self.user, self.address, self.address, self.payment_mode)
        offer = sample_offer(self.user)
        product1 = sample_product(self.user, sample_category(self.user))
        item1 = sample_shopping_item(self.user, product1)
        order.cartItems.add(item1)
        order.offers_applied.add(offer)

        address2 = sample_shipping_address(self.user, name = 'Address 2')
        payment_mode = sample_payment_mode(self.user, title = 'Credit Card')
        product2 = sample_product(self.user, sample_category(self.user, name = 'Category 2'), title = 'Product 2')
        item2 = sample_shopping_item(self.user, product2, count=5)
        offer2 = sample_offer(self.user, title = 'Winter offer 2022')

        payload = {
            'cartItems': [item2.id,],
            'offers_applied': [offer2.id,],
            'shipping_address': address2.printable(),
            'billing_address': address2.printable(),
            'payment_mode': payment_mode.id,
        }
        url = detail_url(order_id=order.id)
        self.client.put(url, payload)
        order.refresh_from_db()
        self.assertEqual(payload['billing_address'], order.billing_address)
        self.assertEqual(payload['payment_mode'], order.payment_mode.id)
        self.assertEqual(payload['shipping_address'], order.shipping_address)
        cart_items = order.cartItems.all()
        offers = order.offers_applied.all()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(len(offers), 1)
        self.assertIn(item2, cart_items)
        self.assertIn(offer2, offers)

    def test_delete_order_normal_user(self):
        """Test deleting order for normal user"""
        order = sample_order(self.user, self.address, self.address, self.payment_mode)
        url = detail_url(order_id=order.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestAdminUserOrderApi(TestCase):
    """Test cases of order for admin user"""

    def setUp(self):
        """Set up for test cases"""
        self.client = APIClient()
        self.user = sample_user(is_staff=True)
        self.client.force_authenticate(self.user)
        self.pmode = sample_payment_mode(self.user, title = 'Payment mode 1')
        self.offer = sample_offer(self.user, title = 'Offer 1')
        self.product = sample_product(self.user, sample_category(self.user, name = 'Category 1'), title = 'Product 1')

    def test_retrieve_orders_admin_user(self):
        """Test retrieve orders for admin user"""
        user1 = sample_user(email='firstuser@gmail.com', password='testpass', is_staff=False)
        address1 = sample_shipping_address(user1)
        order1 = sample_order(user1, address1, address1, self.pmode)
        order1.cartItems.add(sample_shopping_item(user1, self.product))
        order1.offers_applied.add(self.offer)

        user2 = sample_user(email='seconduser@gmail.com', password='testpass', is_staff=False)
        address2 = sample_shipping_address(user2)
        order2 = sample_order(user2, address2, address2, self.pmode)
        order2.cartItems.add(sample_shopping_item(user2, self.product))
        order2.offers_applied.add(self.offer)
        res = self.client.get(ORDER_URL)
        orders = models.Order.objects.all().order_by('-id')
        # print([o.user for o in res.data])
        print(res.data)
        serializer = OrderSerializer(orders, many = True)
        self.assertEqual(res.data, serializer.data)
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from order.serializers import PaymentModeSerializer

PAYMENTMODE_URL = reverse('order:paymentmode-list')

def detail_url(payment_mode_id):
    """Returns the detail url for payment mode id provided"""
    return reverse('order:paymentmode-detail', args=[payment_mode_id])

def sample_user(email='testuser@gmail.com', password='testpassword', is_staff=True):
    return get_user_model().objects.create(email=email, password=password, is_staff=is_staff)

def sample_payment_mode(user, **params):
    """Sample payment mode of provided details"""
    defaults = {
        'title': 'UPI Mode', 
        'desc': 'UPI payment mode', 
        'charges': 0, 
        'enabled': True,
    }
    defaults.update(params)
    return models.PaymentMode.objects.create(user = user, **defaults)


class TestPublicPaymentModeApi(TestCase):
    """Test cases for unauthorized users of Payment Mode api"""

    def setUp(self):
        """Set up test cases"""
        self.client = APIClient()

    def test_retrieve_payment_mode_unauthorized(self):
        """Test retrieving payment mode for unauthenticated user"""
        res = self.client.get(PAYMENTMODE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_paymentmode_unauthorized(self):
        """Test post request for unauthorized user"""
        payload = {
            'title': 'UPI Mode', 
            'desc': 'UPI payment mode', 
            'charges': 0, 
            'enabled': True,
        }
        res = self.client.post(PAYMENTMODE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestNormalUserPaymentModeApi(TestCase):
    """Test cases for payment mode api"""

    def setUp(self):
        """Test case setup"""
        self.client = APIClient()
        self.user = sample_user(is_staff=False)
        self.client.force_authenticate(self.user)

    def test_retrieve_paymentmode_normal_user(self):
        """Test retrieving payment mode"""
        sample_payment_mode(self.user)
        sample_payment_mode(self.user, title = 'Credit Cart')
        res = self.client.get(PAYMENTMODE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        modes = models.PaymentMode.objects.all().order_by('-id')
        serializer = PaymentModeSerializer(modes, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_post_payment_mode_normal_user(self):
        """Test Post payment mode by normal user (non-staff)"""
        payload = {
            'title': 'Debit Card',
            'desc': 'Debit Card payment',
            'charges': 10.14,
            'enabled': True
        }
        res = self.client.post(PAYMENTMODE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_detail_paymentmode(self):
        """Test retrieve detail payment mode"""
        mode = sample_payment_mode(self.user)
        url = detail_url(mode.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        paymentmode = models.PaymentMode.objects.get(id = res.data['id'])
        serializer = PaymentModeSerializer(paymentmode)
        self.assertEqual(res.data, serializer.data)
    
class TestPrivatePaymentModeApi(TestCase):
    """Test cases for payment mode api"""

    def setUp(self):
        """Set up for test cases"""
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_paymentmode_admin(self):
        """Test retrieving payment mode"""
        sample_payment_mode(self.user)
        sample_payment_mode(self.user, title = 'Credit Cart')
        res = self.client.get(PAYMENTMODE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        modes = models.PaymentMode.objects.all().order_by('-id')
        serializer = PaymentModeSerializer(modes, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_post_payment_mode_admin_user(self):
        """Test post payment mode object by admin user"""
        payload = {
            'title': 'UPI',
            'desc': 'UPI Payment mode',
            'charges': 0,
            'enabled': True
        }
        res = self.client.post(PAYMENTMODE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mode = models.PaymentMode.objects.get(id = res.data['id'])
        serializer = PaymentModeSerializer(mode)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_detail_paymentmode(self):
        """Test retrieve detail payment mode"""
        mode = sample_payment_mode(self.user)
        url = detail_url(mode.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        paymentmode = models.PaymentMode.objects.get(id = res.data['id'])
        serializer = PaymentModeSerializer(paymentmode)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_paymentmode_admin(self):
        """Test the partial update of payment mode by admin user"""
        mode = sample_payment_mode(self.user)
        payload = {
            'title': 'Credit Card',
            'desc': 'Credit Card mode payment'
        }
        url = detail_url(mode.id)
        self.client.patch(url, payload)
        mode.refresh_from_db()
        self.assertEqual(payload['title'], mode.title)
        self.assertEqual(payload['desc'], mode.desc)

    def test_full_update_payment_mode_admin(self):
        """Test the full update of payment mode by admin user"""
        mode = sample_payment_mode(self.user)
        payload = {
            'title': 'Credit Card',
            'desc': 'Credit Card mode payment',
            'charges': 10.0,
            'enabled': True
        }
        url = detail_url(mode.id)
        self.client.put(url, payload)
        mode.refresh_from_db()
        for key in payload:
            self.assertEqual(payload[key], getattr(mode, key))

    def test_delete_payment_mode_admin(self):
        """Test deleting payment mode by admin user"""
        mode = sample_payment_mode(self.user)
        url = detail_url(mode.id)
        self.client.delete(url)
        modes = models.PaymentMode.objects.all().filter(id = mode.id)
        self.assertEqual(len(modes), 0)
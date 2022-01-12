from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from offers import serializers
from core import models

OFFER_URL = reverse('offers:offers-list')

def detail_url(offer_id):
    """Returns the detailed url"""
    return reverse('offers:offers-detail', args=[offer_id])

def sample_user(email='testuser@gmail.com', password='testpassword', is_staff=True):
    return get_user_model().objects.create(email=email, password=password, is_staff=is_staff)

def sample_offer(user, **params):
    """Creates a sample offer with provided details"""
    defaults = {
        'title': 'Summer Offer',
        'percentage': 15.0,
        'desc': 'Summer Offer 2021',
        'expiry_date': timezone.make_aware(datetime(2022, 6, 30))
    }
    defaults.update(params)
    return models.Offer.objects.create(user= user, **defaults)


class TestPublicOfferApi(TestCase):
    """Tests for unauthorized access to offer api"""

    def setUp(self):
        """Set up for test cases"""
        self.client = APIClient()

    def test_retrieve_offer_unauthorized(self):
        """Test retriving offer by unauthorized user"""
        user = sample_user(is_staff=True)
        sample_offer(user)
        res = self.client.get(OFFER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        offer = models.Offer.objects.all().order_by('-id')
        serializer = serializers.OfferSerializer(offer, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_post_offer_unauthorized(self):
        payload = {
            'title': 'Summer Offer',
            'percentage': 15.0,
            'desc': 'Summer Offer 2021',
            'expiry_date': timezone.make_aware(datetime(2022, 6, 30))
        }
        res = self.client.post(OFFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_offer_normal_user(self):
        """Test posting offer with normal user"""
        payload = {
            'title': 'Summer Offer',
            'percentage': 15.0,
            'desc': 'Summer Offer 2021',
            'expiry_date': timezone.make_aware(datetime(2022, 6, 30))
        }
        user = sample_user(is_staff=False)
        self.client.force_login(user)
        res = self.client.post(OFFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class TestPrivateOfferApi(TestCase):
    """Test cases for Offer api"""

    def setUp(self):
        """Set up for test cases"""
        self.client = APIClient()
        self.user = sample_user()

        self.client.force_authenticate(self.user)

    def test_retrieve_offers(self):
        """Test retrieve offers"""
        sample_offer(self.user)
        sample_offer(self.user, title = 'Offer 2')
        res = self.client.get(OFFER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        offers = models.Offer.objects.all().order_by('-id')
        serializer = serializers.OfferSerializer(offers, many = True)
        self.assertEqual(res.data, serializer.data)

    def test_post_offer(self):
        payload = {
            'title': 'Summer Offer',
            'percentage': 15.0,
            'desc': 'Summer Offer 2021',
            'expiry_date': timezone.make_aware(datetime(2022, 6, 30))
        }
        res = self.client.post(OFFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        offer = models.Offer.objects.get(id = res.data['id'])
        serializer = serializers.OfferSerializer(offer)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_offer_detailed(self):
        """Test retrieving detailed offer"""
        offer = sample_offer(self.user)
        url = detail_url(offer.id)
        res = self.client.get(url)
        offer = models.Offer.objects.get(id = offer.id)
        serializer = serializers.OfferSerializer(offer)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_offer(self):
        """Test the partial update of offer"""
        payload = {
            'title': 'Winter Offer',
            'desc': 'Winter offer 2022'
        }
        offer = sample_offer(self.user)
        url = detail_url(offer.id)
        self.client.patch(url, payload)
        offer.refresh_from_db()
        self.assertEqual(offer.title, payload['title'])
        self.assertEqual(offer.desc, payload['desc'])

    def test_full_update_offer(self):
        """Test the update of offer"""
        offer = sample_offer(self.user)
        payload = {
            'title': 'Summer Offer',
            'percentage': 15.0,
            'desc': 'Summer Offer 2021',
            'expiry_date': timezone.make_aware(datetime(2022, 6, 30))
        }
        url = detail_url(offer.id)
        self.client.put(url, payload)
        offer.refresh_from_db()
        for key in payload:
            self.assertEqual(payload[key], getattr(offer, key))

    def test_delete_offer(self):
        """Test delete offer"""
        offer = sample_offer(self.user)
        url = detail_url(offer_id=offer.id)
        self.client.delete(url)
        offers = models.Offer.objects.filter(id = offer.id)
        self.assertEqual(len(offers), 0)
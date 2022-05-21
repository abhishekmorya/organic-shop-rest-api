from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category
from product.serializers import CategorySerializer

CATE_URL = reverse('product:category-list')

def detail_url(category_id):
    """Detailed url for update and delete requests"""
    return reverse("product:category-detail", args=[category_id])

def sample_user(**params):
    """Create user with default details if payload not provided"""
    return get_user_model().objects.create_user(**params)

def sample_category(user, **params):
    """Create a sample category with default values if payload not provided"""
    defaults = {
        'name': 'Category',
        'desc': "Category desc"
    }
    defaults.update(params)
    return Category.objects.create(user = user, **defaults)

class TestPublicCategoryApi(TestCase):
    """Test Category api for unauthorized users"""
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_get_successful(self):
        """Test that only logged in users can access category"""
        res = self.client.get(CATE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_post_not_allowed(self):
        """Test that unauthenticated users not allowed to post a category"""
        payload = {
            'name': 'Category',
            'desc': "Category desc"
        }
        
        res = self.client.post(CATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_category_by_normaluser_failed(self):
        """Test that creating category by normal user must failed"""
        payload = {
            'name': 'Bread',
            'desc': 'Bread desc'
        }
        user = sample_user(
            email = 'normal_user@gmail.com',
            password = 'normalpass'
        )
        self.client.force_login(user)
        res = self.client.post(CATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateCategoryApi(TestCase):
    """Test Category api for logged in users"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(
            email = 'test_user@gmail.com',
            password = 'testpassword',
            is_staff = True
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        """Test retrieving all categories"""

        sample_category(user = self.user)
        sample_category(user = self.user, name = 'Category 2')
        
        res = self.client.get(CATE_URL)
        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_by_any_user(self):
        """Test retrieving categories by any user"""
        user = sample_user(
            email = 'test2_user@gmail.com',
            password = 'testpassword'
        )
        sample_category(user = self.user)
        sample_category(user = user, name = 'Category 2', desc = 'Category 2 desc')

        res = self.client.get(CATE_URL)
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_category_by_admin_successful(self):
        """Test successful post by admin user"""
        payload = {
            'name': 'Bread',
            'desc': 'Bread'
        }
        
        res = self.client.post(CATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id = res.data['id'])
        for key in payload:
            self.assertEqual(payload[key], getattr(category, key))

    def test_parial_update_admin_successful(self):
        """Test partial update by admin"""
        category = sample_category(user = self.user)
        url = detail_url(category_id=category.id)

        self.client.patch(url, {'desc': 'Bread desc'})
        category.refresh_from_db()

        self.assertEqual('Bread desc', category.desc)

    def test_full_update_admin_successful(self):
        """Test full update by put method"""
        category = sample_category(user = self.user)
        url = detail_url(category_id=category.id)
        payload = {
            'name': 'Bread',
            'desc': 'Bread desc'
        }
        self.client.put(url, payload)
        category.refresh_from_db()
        self.assertEqual(payload['name'], category.name)
        self.assertEqual(payload['desc'], category.desc)

    def test_delete_admin_successful(self):
        """Test delete of a category"""
        category1 = sample_category(user = self.user)
        category2 = sample_category(user = self.user, name = 'Bread', desc = 'Bread desc')

        url = detail_url(category_id=category2.id)
        self.client.delete(url)
        categories = Category.objects.all()
        serializer1 = CategorySerializer(categories, many = True)
        serializer2 = CategorySerializer(category1)
        self.assertEqual(len(serializer1.data), 1)
        self.assertIn(serializer2.data, serializer1.data)
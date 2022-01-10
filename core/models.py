from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

import uuid
import os
import re
from PIL import Image

from django.db import models
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, ManyToManyField


def uploaded_images_for_products(instance, filepath):
    """Generate new path for upoaded images to products"""
    ext = filepath.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/products/', filename)


def validate_pincode(value):
    """Validates the pincode for 6 digits and first non-zero digit"""
    regex = "^[1-9]{1}[0-9]{5}$"
    if not bool(re.search(regex, value)):
        raise ValidationError('Invalid pincode')


class UserManager(BaseUserManager):
    """
    User Manager for creating User and super user
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create a normal user"""

        if not email:
            raise ValueError("Email field is required")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create a super user"""

        if not email:
            raise ValueError("Email field is required")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self.create_user(email, password, **extra_fields)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Model for user object"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class UserAddress(models.Model):
    """Model for Address object"""

    HOME = 0
    WORK = 1
    OTHER = 2

    ADDRESS_TYPE_CHOICES = (
        (HOME, 'Home'),
        (WORK, 'Work'),
        (OTHER, 'Other'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, blank=False)
    line1 = models.CharField(max_length=255, blank=False)
    line2 = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=False)
    district = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    pincode = models.CharField(max_length=6, blank=False,
                               validators=[validate_pincode, ]
                               )
    addressType = models.IntegerField(
        default=HOME, choices=ADDRESS_TYPE_CHOICES)

    def __str__(self):
        return f'name: {self.name}, district: {self.district}, state: {self.state}, pincode: {self.pincode}'


class Category(models.Model):
    """Model for Category object"""

    name = models.CharField(max_length=255, unique=True)
    desc = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Model for Product object"""

    UNIT = 0
    KG = 1
    LTR = 2
    GM = 3

    UNIT_CHOICES = (
        (UNIT, 'unit'),
        (KG, 'kg'),
        (LTR, 'ltr'),
        (GM, 'g'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    desc = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(
        blank=False,
        validators=[MinValueValidator(0.00)]
    )
    quantity = models.IntegerField(
        blank=False,
        validators=[MinValueValidator(1)]
    )
    unit = models.IntegerField(choices=UNIT_CHOICES, default=UNIT)
    image = models.ImageField(
        blank=True, upload_to=uploaded_images_for_products)

    def __str__(self):
        """String representation of Product object"""
        return self.title


class UserDetails(models.Model):
    """User details object"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        primary_key=True
    )
    selectedAddress = models.ForeignKey(
        UserAddress,
        models.CASCADE,
    )


class ShoppingCart(models.Model):
    """Shopping Cart object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.IntegerField(blank=False, validators=[MinValueValidator(1)])

    def __str__(self):
        """String representation of Shopping Cart"""
        return f'{str(self.product)}, {self.count}'


class PaymentMode(models.Model):
    """Model for payment mode object"""
    title = models.CharField(max_length=100, unique=True)
    desc = models.CharField(max_length=255)
    charges = models.FloatField(validators=[MinValueValidator(0)])
    enabled = models.BooleanField(default=False)

    def __str__(self):
        """String reprentation of Payment Mode object"""
        return self.title


class Offer(models.Model):
    """Model for offer object"""
    title = models.CharField(max_length=255)
    percentage = models.FloatField(blank=False)
    desc = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        """String representation of Offer object"""
        return self.title


class Order(models.Model):
    """Model for Order object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    cartItems = ManyToManyField(ShoppingCart)
    offers_applied = models.ManyToManyField(Offer)
    ordered_on = models.DateTimeField(auto_now_add=True)
    shipping_address = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    payment_mode = models.ForeignKey(PaymentMode, on_delete = models.PROTECT)


class PriceDetail(models.Model):
    """Model for Price detail object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE
    )
    delievery_charges = models.FloatField()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

import re

from django.db import models
from django.conf import settings

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
    pincode = models.CharField(max_length = 6, blank=False,
        validators=[validate_pincode,]
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
    image = models.ImageField(blank = True)

    def __str__(self):
        """String representation of Product object"""
        return self.title



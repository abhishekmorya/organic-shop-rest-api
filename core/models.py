from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from rest_framework.compat import MaxValueValidator


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
    pincode = models.CharField(max_length=6, blank=False)
    addressType = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])

    def __str__(self):
        return f'name: {self.name}, district: {self.district}, state: {self.state}, pincode: {self.pincode}'


class Category(models.Model):
    """Model for Category object"""

    name = models.CharField(max_length=255, unique=True)
    desc = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"name: {self.name}, desc: {self.desc}"

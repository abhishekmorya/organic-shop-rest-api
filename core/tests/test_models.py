from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Test class for models"""

    def test_create_user_with_email_successful(self):
        """Test creating user with new email"""

        email = "abhishek@gmail.com"
        password = 'testpassword'

        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_with_email_normalize(self):
        """Test the new user created with email normalized"""

        email = "abhishek@GMAIL.COM"
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_mail(self):
        """Test creating user with no email raise Value error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email = None, 
                password = 'Testpassword'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        email = 'abhishek@gmail.com'
        password = 'testpassword'

        user = get_user_model().objects.create_superuser(
            email = email,
            password = password
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    
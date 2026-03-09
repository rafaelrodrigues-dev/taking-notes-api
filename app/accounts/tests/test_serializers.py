from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserSerializer, validate_password, validate_username

User = get_user_model()


class UserSerializerTests(TestCase):
    def test_validate_password_allows_valid_password(self):
        # Should not raise for a valid password (alphanumeric and >= 8 characters)
        validate_password('abc12345')

    def test_validate_password_rejects_short_password(self):
        with self.assertRaises(serializers.ValidationError):
            validate_password('a1B2c3')

    def test_validate_password_rejects_non_alphanumeric_password(self):
        with self.assertRaises(serializers.ValidationError):
            validate_password('password!')

    def test_validate_username_allows_valid_username(self):
        # Only letters, numbers, and underscores are allowed
        validate_username('valid_user_123')

    def test_validate_username_rejects_invalid_username(self):
        with self.assertRaises(serializers.ValidationError):
            validate_username('invalid user')

    def test_user_serializer_create_sets_password_hash(self):
        data = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'alpha1234',
            'first_name': 'New',
            'last_name': 'User',
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        user = serializer.save()

        self.assertTrue(User.objects.filter(username='new_user').exists())
        self.assertNotEqual(user.password, data['password'])
        self.assertTrue(user.check_password(data['password']))
        # Password must not be included in serialized output
        self.assertNotIn('password', serializer.data)

    def test_user_serializer_update_changes_password_when_provided(self):
        user = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='oldpass123'
        )

        serializer = UserSerializer(user, data={'password': 'newpass123'}, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        updated_user = serializer.save()

        self.assertTrue(updated_user.check_password('newpass123'))

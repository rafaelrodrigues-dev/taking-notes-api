from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserViewTests(APITestCase):
    def setUp(self):
        # User test
        self.user1 = User.objects.create_user(
            username='user_one', email='user1@example.com', password='pass1234'
        )
        self.user2 = User.objects.create_user(
            username='user_two', email='user2@example.com', password='pass1234'
        )
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client = APIClient()

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_user(self):
        payload = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'alpha1234',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(reverse('user-create'), payload)
        assert response.status_code == status.HTTP_201_CREATED
        # Create user in database
        assert User.objects.filter(username='new_user').exists()
        # Password must be not returned in response (write_only)
        assert 'password' not in response.data
    
    def test_retrieve_self(self):
        self.auth(self.token1)
        url = reverse('user-detail')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == self.user1.username

    def test_patch_own_user(self):
        self.auth(self.token1)
        url = reverse('user-detail')
        payload = {'first_name': 'Updated'}
        response = self.client.patch(url, payload)
        assert response.status_code == status.HTTP_200_OK
        self.user1.refresh_from_db()
        assert self.user1.first_name == 'Updated'

    def test_delete_own_user(self):
        self.auth(self.token1)
        url = reverse('user-detail')
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=self.user1.pk).exists()

    def test_put_not_allowed(self):
        self.auth(self.token1)
        url = reverse('user-detail')
        payload = {
            'username': 'ignored',
            'email': 'ignored@example.com',
            'first_name': 'Ignored',
            'last_name': 'Ignored'
        }
        response = self.client.put(url, payload)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
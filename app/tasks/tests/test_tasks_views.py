from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


class TaskViewSetTest(APITestCase):
    def setUp(self):
        # Create a primary user for testing
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.token = Token.objects.create(user=self.user)

        # Create a second user to test data isolation
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.other_token = Token.objects.create(user=self.other_user)

        # Create a task belonging to the primary user
        self.task = Task.objects.create(
            title='My Task',
            description='Description of my task',
            user=self.user
        )

        # Create a task belonging to the other user
        self.other_task = Task.objects.create(
            title='Other Task',
            description='Description of other task',
            user=self.other_user
        )

        # Authenticate the primary user by adding the Token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # URLs
        self.list_url = reverse('task-list')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.task.pk})

    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tasks(self):
        """Test retrieving a list of tasks for the authenticated user."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see 1 task (the one belonging to self.user)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'My Task')

    def test_retrieve_task(self):
        """Test retrieving a single task detail."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Task')

    def test_create_task(self):
        """Test creating a new task."""
        data = {
            'title': 'New Task',
            'description': 'New task description'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)  # 2 existing + 1 new
        self.assertEqual(Task.objects.get(title='New Task').user, self.user)

    def test_update_task(self):
        """Test updating an existing task (PATCH)."""
        data = {'title': 'Updated Title'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Title')

    def test_delete_task(self):
        """Test deleting a task."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_user_cannot_access_other_users_task(self):
        """Test that a user cannot retrieve a task belonging to another user."""
        other_task_url = reverse('task-detail', kwargs={'pk': self.other_task.pk})
        response = self.client.get(other_task_url)
        # Should return 404 because get_queryset filters it out
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_other_users_task(self):
        """Test that a user cannot update a task belonging to another user."""
        other_task_url = reverse('task-detail', kwargs={'pk': self.other_task.pk})
        data = {'title': 'Hacked Title'}
        response = self.client.patch(other_task_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_task.refresh_from_db()
        self.assertNotEqual(self.other_task.title, 'Hacked Title')

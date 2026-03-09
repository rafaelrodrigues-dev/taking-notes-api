from django.test import TestCase
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


class TaskModelTest(TestCase):
    def setUp(self):
        # Create a user to associate with the task
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        # Create a sample task
        self.task = Task.objects.create(
            title='Test Task',
            description='This is the description of the test task.',
            user=self.user
        )

    def test_task_creation(self):
        """Test that the task is correctly created with the provided attributes."""
        self.assertTrue(isinstance(self.task, Task))
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is the description of the test task.')
        self.assertEqual(self.task.user, self.user)

        # completed defaults to False
        self.assertFalse(self.task.completed)

        # created_at is automatically generated, so just check it is not None
        self.assertIsNotNone(self.task.created_at)

    def test_task_str_representation(self):
        """Test that the __str__ method returns the task title."""
        self.assertEqual(str(self.task), 'Test Task')

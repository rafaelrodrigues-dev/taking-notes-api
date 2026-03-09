from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Task
from .serializers import TaskSerializer


class Pagination(PageNumberPagination):
    page_size = 10


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    http_method_names = ['get', 'options', 'head', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Task.objects.filter(user_id=self.request.user.id).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

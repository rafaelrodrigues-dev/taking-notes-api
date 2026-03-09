from django.urls import path
from .views import UserCreateAPIView, UserAPIView

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-create'),
    path('me/', UserAPIView.as_view(), name='user-detail'),
]
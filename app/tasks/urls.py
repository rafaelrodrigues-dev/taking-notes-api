from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', views.TaskViewSet,'task')

urlpatterns = router.urls
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from tasks.views import TaskViewSet

router = SimpleRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]

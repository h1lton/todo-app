from rest_framework_nested import routers

from .views import BoardViewSet, TaskViewSet

urlpatterns = []

board_router = routers.DefaultRouter()
board_router.register('', BoardViewSet, basename='board')
urlpatterns += board_router.urls

task_router = routers.NestedDefaultRouter(board_router, '', lookup='board')
task_router.register('task', TaskViewSet, basename='task')
urlpatterns += task_router.urls

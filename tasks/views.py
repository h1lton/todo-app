from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .models import Task
from .permissions import IsOwner
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [*api_settings.DEFAULT_PERMISSION_CLASSES, IsOwner]

    def get_queryset(self):
        return self.request.user.task_set.all()

    @action(detail=True, methods=['POST'])
    def close(self, request, pk=None):
        task = self.get_object()
        task.close = not task.close
        task.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

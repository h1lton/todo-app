from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from tasks.models import Task
from tasks.permissions import IsOwner
from tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return self.request.user.task_set.all()

    @action(detail=True)
    def close(self, request, pk=None):
        task = self.get_object()
        task.close = not task.close
        task.save()
        return Response(status=status.HTTP_200_OK)

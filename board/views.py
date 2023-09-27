from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .permissions import IsOwner, IsMember
from .serializers import ListBoardSerializer, DetailBoardSerializer, ListTaskSerializer, DetailTaskSerializer
from .models import Board, Task


class BoardViewSet(ModelViewSet):
    permission_classes = [*api_settings.DEFAULT_PERMISSION_CLASSES, IsOwner]

    def get_serializer_class(self):
        if self.action == 'list':
            return ListBoardSerializer
        else:
            return DetailBoardSerializer

    def get_queryset(self):
        return Board.objects.all_user_boards(self.request.user)


class TaskViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return ListTaskSerializer
        else:
            return DetailTaskSerializer

    permission_classes = [*api_settings.DEFAULT_PERMISSION_CLASSES, IsMember]

    def get_queryset(self):
        return Task.objects.filter(board=self.kwargs['board_pk'])

    @action(detail=True, methods=['post'])
    def close(self, request, board_pk=None, pk=None):
        task = self.get_object()
        task.is_close = not task.is_close
        task.save()
        return Response(status=204)

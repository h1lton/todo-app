from rest_framework import permissions
from rest_framework.permissions import BasePermission

from board.models import Board


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsMember(BasePermission):
    def has_permission(self, request, view):
        return Board.objects.is_member(view.kwargs['board_pk'], request.user)

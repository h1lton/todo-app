from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class BoardManager(models.Manager):
    def all_user_boards(self, user):
        return self.filter(Q(users__in=[user]) | Q(owner=user))

    def is_member(self, board_id, user):
        return self.filter(Q(id=board_id), Q(users__in=[user]) | Q(owner=user)).exists()


class Board(models.Model):
    name = models.CharField(max_length=25)
    users = models.ManyToManyField(User, related_name='users', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')

    objects = BoardManager()


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_close = models.BooleanField(default=False)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=500, null=True, blank=True)

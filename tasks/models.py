from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_close = models.BooleanField(default=False)
    content = models.CharField(max_length=500)

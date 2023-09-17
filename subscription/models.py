import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class PlanManager(models.Manager):
    def all_active(self):
        return self.filter(
            Q(start_date__lte=timezone.now()) | Q(start_date__isnull=True),
            Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True),
            is_active=True
        )


class Plan(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    discount = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(100)])
    # discount пока-что не используется
    price = models.PositiveIntegerField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    objects = PlanManager()

    def clean(self):  # tested
        if self.start_date and self.start_date < timezone.now():
            raise ValidationError({'start_date': 'Дата начала действия цены должна быть в будущем.'})
        if self.end_date and self.end_date < timezone.now():
            raise ValidationError({'end_date': 'Дата окончания действия цены должна быть в будущем.'})
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'Действие цены не может закончиться раньше чем начаться.'})

    def buy(self, user):
        return Subscription.objects.create(
            user=user,
            end_date=timezone.now() + datetime.timedelta(days=self.duration),
            purchase_price=self.price,
            plan=self
        )


class SubscriptionManager(models.Manager):
    def get_active_subscription(self, user):
        return self.filter(user=user, end_date__gt=timezone.now()).first()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    purchase_price = models.PositiveIntegerField()
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)

    objects = SubscriptionManager()

    def clean(self):
        if self.end_date <= timezone.now():
            raise ValidationError({"end_date": "Дата окончания подписки должна быть в будущем."})

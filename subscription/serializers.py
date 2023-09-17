from rest_framework import serializers
from .models import *


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        exclude = ('user',)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        exclude = ('is_active',)

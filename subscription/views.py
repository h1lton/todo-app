from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Subscription, Plan
from .serializers import SubscriptionSerializer, PlanSerializer


class ActiveSubscriptionView(RetrieveAPIView):
    serializer_class = SubscriptionSerializer

    def get_object(self):
        return Subscription.objects.get_active_subscription(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        active_subscription = self.get_object()
        if active_subscription:
            serializer = self.get_serializer(active_subscription)
            return Response(serializer.data)
        else:
            data = {"detail": "Активная подписка не найдена."}
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class ActivePlanViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = PlanSerializer

    def get_queryset(self):
        return Plan.objects.all_active()

    @action(detail=True, methods=['POST'])
    def buy(self, request, pk=None):
        plan = self.get_object()
        sub = plan.buy(request.user)

        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

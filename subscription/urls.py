from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ActiveSubscriptionView, ActivePlanViewSet

router = DefaultRouter()
router.register('plan', ActivePlanViewSet, basename='plan')
urlpatterns = router.urls

urlpatterns += [
    path('active/', ActiveSubscriptionView.as_view(), name='active-subscription'),
]

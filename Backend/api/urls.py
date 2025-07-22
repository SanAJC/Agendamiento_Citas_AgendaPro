from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, BusinessHourViewSet, ServiceViewSet, AppointmentViewSet, SubscriptionViewSet, PlanViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'business', BusinessViewSet, basename='business')
router.register(r'business-hour', BusinessHourViewSet, basename='business-hour')
router.register(r'service', ServiceViewSet, basename='service')
router.register(r'appointment', AppointmentViewSet, basename='appointment')
router.register(r'subscription', SubscriptionViewSet, basename='subscription')
router.register(r'plan', PlanViewSet, basename='plan')
router.register(r'notification', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]

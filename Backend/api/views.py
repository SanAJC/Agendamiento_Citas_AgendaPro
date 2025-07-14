from django.shortcuts import render
from rest_framework import viewsets
from .models import Business, Service, Appointment, Subscription, Plan, Payment, Notification , BusinessHour
from .serializers import BusinessSerializer, ServiceSerializer, AppointmentSerializer, SubscriptionSerializer, PlanSerializer, PaymentSerializer, NotificationSerializer , BusinessHourSerializer
from services.mercado_pago import create_subscription, update_subscription
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class BusinessHourViewSet(viewsets.ModelViewSet):
    queryset = BusinessHour.objects.all()
    serializer_class = BusinessHourSerializer
    

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

@permission_classes([IsAuthenticated])
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def perform_create(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        try:
            result = create_subscription(subscription.plan.mp_plan_id, subscription.customer.email, subscription.card_token_id)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error al crear la suscripción en MP: {e}")
            subscription.delete()
        
    def perform_update(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        try:
            result = update_subscription(subscription.mp_subscription_id, subscription.customer.email, subscription.card_token_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error al actualizar la suscripción en MP: {e}")
            subscription.delete()

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

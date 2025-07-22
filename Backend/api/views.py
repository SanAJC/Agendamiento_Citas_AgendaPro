from typing import override
from django.shortcuts import render
from rest_framework import viewsets
from .models import Business, Service, Appointment, Subscription, Plan, Notification , BusinessHour
from .serializers import BusinessSerializer, ServiceSerializer, AppointmentSerializer, SubscriptionSerializer, PlanSerializer, NotificationSerializer , BusinessHourSerializer
from services.mercado_pago import create_subscription, update_subscription
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, action
from rest_framework.response import Response
from rest_framework import status
from services.google_calendar import GoogleCalendarService
from allauth.socialaccount.models import SocialAccount

@permission_classes([IsAuthenticated])
class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

@permission_classes([IsAuthenticated])
class BusinessHourViewSet(viewsets.ModelViewSet):
    queryset = BusinessHour.objects.all()
    serializer_class = BusinessHourSerializer
    
@permission_classes([IsAuthenticated])
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

@permission_classes([IsAuthenticated])
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        appointment = serializer.save()
        self._sync_google_calendar(appointment)
        self._create_notification(appointment, 'confirmada')

        user = appointment.customer
        has_google_account = SocialAccount.objects.filter(
            user=user, 
            provider='google'
        ).exists()

        if not has_google_account:
            Notification.objects.create(
                user=user,
                mensaje="¿Quieres recibir recordatorios en Google Calendar? Vincula tu cuenta de Google para sincronizar tus citas automáticamente.",
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _sync_google_calendar(self, appointment):
        try:
            # Verificar si el usuario tiene una cuenta de Google vinculada
            if not hasattr(appointment.customer, 'socialaccount_set'):
                print("No se encontró la cuenta de Google del usuario")
                return
            
            social_account = SocialAccount.objects.filter(user=appointment.customer, provider='google').first()
            if not social_account:
                print(f"El usuario {appointment.customer.username} no tiene una cuenta de Google vinculada")
                return
            
            # Verificar si ya existe un evento en Google Calendar para esta reserva
            if appointment.google_calendar_event_id:
                result = GoogleCalendarService.update_calendar_event(
                    appointment.customer, 
                    appointment, 
                    appointment.google_calendar_event_id
                )
                if result:
                    print(f"Evento de Google Calendar actualizado correctamente para la reserva {appointment.id}")
                else:
                    print(f"No se pudo actualizar el evento de Google Calendar para la reserva {appointment.id}")
            else:
                # Crear un nuevo evento en Google Calendar
                event_id = GoogleCalendarService.create_calendar_event(
                    appointment.customer, 
                    appointment
                )
                if event_id:
                    print(f"Evento de Google Calendar creado correctamente con ID: {event_id}")
                    appointment.google_calendar_event_id = event_id
                    appointment.save(update_fields=['google_calendar_event_id'])
                else:
                    print(f"No se pudo crear el evento de Google Calendar para la reserva {appointment.id}")
        except Exception as e:
            print(f"Error al sincronizar la cita en Google Calendar: {e}")
    
    def _create_notification(self, appointment, action_type):
        mensaje = f"Tu cita ha sido {action_type}. Fecha: {appointment.date.strftime('%d/%m/%Y')}, " \
                 f"Hora: {appointment.time.strftime('%H:%M')}"
        
        Notification.objects.create(
            user=appointment.customer,
            mensaje=mensaje
        )
    
    def perform_update(self, serializer):
        appointment = serializer.save()
        self._sync_google_calendar(appointment)
        self._create_notification(appointment, "actualizada")
    
    def perform_destroy(self, instance):
        if instance.google_calendar_event_id:
            if hasattr(instance.customer, 'socialaccount_set'):
                social_account = SocialAccount.objects.filter(user=instance.customer, provider='google').first()
                if social_account:
                    GoogleCalendarService.delete_calendar_event(instance.customer, instance.google_calendar_event_id)
        
        self._create_notification(instance, "cancelada")
        super().perform_destroy(instance)

    @action(detail=False, methods=['get'], url_path='my-reservations')
    def my_reservations(self, request):
        user = request.user
        reservations = Appointment.objects.filter(customer=user)
        serializer = AppointmentSerializer(reservations, many=True)
        return Response(serializer.data)

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

@permission_classes([IsAuthenticated])
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


@permission_classes([IsAuthenticated])
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')

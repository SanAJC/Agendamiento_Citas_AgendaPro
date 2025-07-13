from rest_framework import serializers
from .models import Business, Service, Appointment, Subscription, Plan, Payment, Notification, BusinessHour
from authentication.models import User
from authentication.serializers import UserSerializer

class BusinessSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    logo = serializers.SerializerMethodField()
    class Meta:
        model = Business
        fields = '__all__'
    
    def get_logo (self, obj ):
        return obj.logo.url if obj.logo else None


class BusinessHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHour
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    class Meta:
        model = Service
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    class Meta:
        model = Appointment
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    plan = PlanSerializer(read_only=True)
    class Meta:
        model = Subscription
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = '__all__'

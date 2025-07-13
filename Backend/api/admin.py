from django.contrib import admin
from .models import Plan, Business, BusinessHour, Service, Appointment, Subscription, Payment, Notification

admin.site.register(Plan)
admin.site.register(Business)
admin.site.register(BusinessHour)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Subscription)
admin.site.register(Payment)
admin.site.register(Notification)


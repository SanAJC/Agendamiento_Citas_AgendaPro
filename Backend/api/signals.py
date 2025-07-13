from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Plan
from services.mercado_pago import create_plan

@receiver(post_save, sender=Plan)
def post_save_plan(sender, instance: Plan, created, **kwargs):
    if created and not instance.mp_plan_id:
        create_plan(instance)

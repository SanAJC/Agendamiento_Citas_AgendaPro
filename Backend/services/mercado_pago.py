import requests
from django.conf import settings
from api.models import Plan
import logging

logger = logging.getLogger(__name__)

MP_BASE_URL = "https://api.mercadopago.com"
MP_TOKEN = settings.MERCADOPAGO_ACCESS_TOKEN  # tu Access Token

def create_plan(plan: Plan):
    url = f"{MP_BASE_URL}/preapproval_plan"
    headers = {
        "Authorization": f"Bearer {MP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "reason": plan.name,
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "repetitions": 12,
            "transaction_amount": int(plan.price),
            "currency_id": "COP"   
        },
        "back_url": "https://www.yoursite.com"
    }

    resp = requests.post(url, json=payload, headers=headers)
    data = resp.json()
    logger.debug("MP /preapproval_plan response: %s", data)

    if resp.status_code == 201 and "id" in data:
        plan.mp_plan_id = data["id"]
        plan.save()
        logger.info("Plan creado en MP con id %s", data["id"])
        return plan
    else:
        error = data.get("message") or data
        logger.error("Error creando plan en MP: %s", error)
        raise Exception(f"MP plan error: {error}")


# =========================================
# payment/urls.py
# =========================================

from django.urls import path

from rideshare.views import (
    paystack_webhook
)

urlpatterns = [

    path("paystack/webhook/", paystack_webhook, name="paystack_webhook")
]
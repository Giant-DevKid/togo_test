# =========================================
# payment/urls.py
# =========================================

from django.urls import path

from rideshare.views import (
    paystack_webhook, paystack_callback_page, PaystackCallbackAPIView
)

urlpatterns = [

    path("paystack/webhook/", paystack_webhook, name="paystack_webhook"),
    path("paystack/callback/", paystack_callback_page, name="paystack_callback"),
    path("payments/paystack/callback/", PaystackCallbackAPIView.as_view(), name="payment-callback"),
]
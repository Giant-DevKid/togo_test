import os
import json
import hmac
import hashlib
from django.db import transaction


from django.http import (

    HttpResponse,

    JsonResponse
)

from django.utils import timezone

from django.views.decorators.csrf import (
    csrf_exempt
)

from rideshare.models import (
    Payment
)

from conversation.services.notifications import (

    send_passenger_payment_success_message,

    send_rider_payment_success_message
)


@csrf_exempt
def paystack_webhook(
    request
):

    # =====================================
    # VERIFY SIGNATURE
    # =====================================

    signature = request.headers.get(
        "x-paystack-signature"
    )

    computed_signature = hmac.new(

        os.getenv("PAYSTACK_SECRET_KEY").encode(),

        request.body,

        hashlib.sha512

    ).hexdigest()

    if signature != computed_signature:

        return HttpResponse(
            status=400
        )

    # =====================================
    # PARSE PAYLOAD
    # =====================================

    payload = json.loads(
        request.body
    )

    event = payload.get("event")

    # =====================================
    # HANDLE SUCCESS ONLY
    # =====================================

    if event != "charge.success":

        return HttpResponse(
            status=200
        )

    data = payload.get(
        "data",
        {}
    )

    reference = data.get(
        "reference"
    )

    if not reference:

        return HttpResponse(
            status=400
        )

    # =====================================
    # FIND PAYMENT
    # =====================================

    payment = (

        Payment.objects
        .select_related(

            "booking",

            "passenger",

            "rider"
        )
        .filter(
            payment_reference=reference
        )
        .first()
    )

    if not payment:

        return HttpResponse(
            status=404
        )

    # =====================================
    # PREVENT DOUBLE PROCESSING
    # =====================================

    if payment.status == "SUCCESS":

        return HttpResponse(
            status=200
        )

    # =====================================
    # UPDATE PAYMENT
    # =====================================

    with transaction.atomic():

        payment.status = "SUCCESS"

        payment.gateway_response = (
            data
        )

        payment.paid_at = (
            timezone.now()
        )

        payment.save()

        # =====================================
        # UPDATE BOOKING
        # =====================================

        booking = payment.booking

        booking.status ="CONFIRMED"
    
        booking.save()

    # =====================================
    # NOTIFY PASSENGER
    # =====================================

    send_passenger_payment_success_message(
        booking
    )

    # =====================================
    # NOTIFY RIDER
    # =====================================

    send_rider_payment_success_message(
        booking
    )

    return JsonResponse({

        "success": True
    })
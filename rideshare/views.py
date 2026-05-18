# =========================================
# payment/views.py
# =========================================

import hmac
import hashlib
import json

from django.conf import settings

from django.http import (
    HttpResponse,
    JsonResponse
)

from django.views.decorators.csrf import (
    csrf_exempt
)

from rideshare.models import (
    RideBooking
)

from conversation.services.message_service import (
    send_text
)

from conversation.services.notifications import (
    send_passenger_payment_success_message, send_rider_payment_success_message
)


# =========================================
# PAYSTACK WEBHOOK
# =========================================
@csrf_exempt
def paystack_webhook(
    request
):

    # =====================================
    # VERIFY PAYSTACK SIGNATURE
    # =====================================

    signature = request.headers.get(
        "x-paystack-signature"
    )

    computed_signature = hmac.new(

        settings.PAYSTACK_SECRET_KEY.encode(
            "utf-8"
        ),

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
    # ONLY HANDLE SUCCESSFUL PAYMENTS
    # =====================================

    if event != "charge.success":

        return HttpResponse(
            status=200
        )

    data = payload.get("data", {})

    metadata = data.get(
        "metadata",
        {}
    )

    booking_id = metadata.get(
        "booking_id"
    )

    if not booking_id:

        return HttpResponse(
            status=400
        )

    # =====================================
    # GET BOOKING
    # =====================================

    booking = (

        RideBooking.objects
        .select_related(

            "passenger",

            "selected_rider"
        )
        .filter(
            id=booking_id
        )
        .first()
    )

    if not booking:

        return HttpResponse(
            status=404
        )

    # =====================================
    # PREVENT DUPLICATE PROCESSING
    # =====================================

    if booking.status == "CONFIRMED":

        return HttpResponse(
            status=200
        )

    # =====================================
    # CONFIRM BOOKING
    # =====================================

    booking.status = (
        "CONFIRMED"
    )

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
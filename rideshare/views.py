import os
import json
import hmac
import hashlib
from django.db import transaction
from django.shortcuts import (render, get_object_or_404)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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
from conversation.models import ConversationSession
from conversation.services.session_service import reset_session

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
    # RESET PASSENGER SESSION
    # =====================================

    passenger_session = (

        ConversationSession.objects
        .filter(
            user=booking.passenger
        )
        .first()
    )

    if passenger_session:

        reset_session(
            passenger_session
        )


    # =====================================
    # NOTIFY PASSENGER
    # =====================================
    

    send_passenger_payment_success_message(
        booking
    )

    # =====================================
    # RESET PASSENGER SESSION
    # =====================================

    rider_session = (

        ConversationSession.objects
        .filter(
            user=booking.selected_rider
        )
        .first()
    )

    if rider_session:

        reset_session(
            rider_session
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



def paystack_callback_page(request):

    reference = request.GET.get(
        "reference"
    )

    trxref = request.GET.get(
        "trxref"
    )
    payment = get_object_or_404(

        Payment.objects.select_related(

            "booking",

            "passenger",

            "rider"
        ),

        payment_reference=reference
    )

    booking = payment.booking

    context = {

        "reference": reference,

        "trxref": trxref,
        "payment": payment,

        "booking": booking
    }

    return render(

        request,

        "payment/paystack_callback.html",

        context
    )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Payment


class PaystackCallbackAPIView(APIView):
    """
    Handle Paystack callback verification.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        reference = request.GET.get("reference")
        trxref = request.GET.get("trxref")

        if not reference:
            return Response(
                {
                    "success": False,
                    "message": "Payment reference is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(
            Payment.objects.select_related(
                "booking",
                "passenger",
                "rider",
            ),
            payment_reference=reference,
        )

        booking = payment.booking

        data = {
            "success": True,
            "reference": reference,
            "trxref": trxref,
            "payment": {
                "id": payment.id,
                "payment_reference": payment.payment_reference,
                "amount": payment.amount,
                "status": payment.status,
            },
            "booking": {
                "id": booking.id,
            },
        }

        return Response(data, status=status.HTTP_200_OK)
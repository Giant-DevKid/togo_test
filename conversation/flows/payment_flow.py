# conversation/flows/payment_flow.py

from rideshare.models import (
    RideBooking
)

from conversation.services.message_service import (
    send_text
)

from rideshare.utils.paystack_service import (
    initialize_paystack_payment
)


def handle_payment_flow(
    session,
    message
):

    normalized_message = (
        message.strip().lower()
    )

    booking_id = (

        session.context["data"]
        .get("booking_id")
    )

    booking = RideBooking.objects.filter(
        id=booking_id
    ).first()

    if not booking:

        return send_text(

            session.phone_number,

            "Booking not found."
        )

    # =====================================
    # PAY NOW
    # =====================================

    if normalized_message == "pay now":

        payment  = (
            initialize_paystack_payment(
                booking
            )
        )

        return send_text(

            session.phone_number,

            (
                "💳 Complete payment below:\n\n"

                f"{payment.authorization_url}"
            )
        )

    # =====================================
    # CANCEL RIDE
    # =====================================

    if normalized_message == "cancel ride":

        booking.status = (
            "CANCELLED"
        )

        booking.save()

        session.context = {

            "active_flow": None,

            "step": None,

            "data": {}
        }

        session.save()

        return send_text(

            session.phone_number,

            (
                "Ride cancelled successfully."
            )
        )

    return send_text(

        session.phone_number,

        (
            "Reply with:\n\n"

            "• pay now\n"

            "• cancel ride"
        )
    )
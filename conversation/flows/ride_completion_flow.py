from rideshare.models import (
    RideBooking
)

from rideshare.services import (
    generate_ride_otp
)
from django.utils import timezone


from conversation.services.message_service import (
    send_text
)

from rideshare.utils.paystack_service import (
    release_rider_payment
)


def request_ride_otp(
    session,
    booking_id
):

    booking = (

        RideBooking.objects
        .filter(

            id=booking_id,

            selected_rider=session.user,

            status__in=[

                "CONFIRMED",

                "IN_PROGRESS"
            ]
        )
        .select_related(
            "passenger"
        )
        .first()
    )

    if not booking:

        return send_text(

            session.phone_number,

            (
                "Ride booking not found."
            )
        )

    otp = generate_ride_otp(
        booking
    )

    # =====================================
    # SEND OTP TO PASSENGER
    # =====================================

    send_text(

        booking.passenger.phone_no,

        (
            "🔐 Ride Completion OTP\n\n"

            f"Your OTP is: {otp}\n\n"

            "Please give this OTP "
            "to your rider after "
            "you reach your destination."
        )
    )

    return send_text(

        session.phone_number,

        (
            "OTP sent to passenger "
            "successfully."
        )
    )


def verify_ride_otp(
    session,
    booking_id,
    otp
):

    booking = (

        RideBooking.objects
        .filter(

            id=booking_id,

            selected_rider=session.user,

            status="OTP_PENDING"
        )
        .select_related(

            "passenger",

            "selected_rider"
        )
        .first()
    )

    if not booking:

        return send_text(

            session.phone_number,

            (
                "Ride booking not found."
            )
        )

    # =====================================
    # INVALID OTP
    # =====================================

    if (

        booking.ride_completion_otp
        != otp
    ):

        return send_text(

            session.phone_number,

            "Invalid OTP."
        )

    # =====================================
    # COMPLETE RIDE
    # =====================================

    booking.status = (
        "COMPLETED"
    )

    booking.otp_verified_at = (
        timezone.now()
    )

    booking.save()

    # =====================================
    # RELEASE RIDER PAYMENT
    # =====================================

    release_rider_payment(
        booking
    )

    # =====================================
    # NOTIFY PASSENGER
    # =====================================

    send_text(

        booking.passenger.phone_no,

        (
            "✅ Ride Completed\n\n"

            "Thank you for riding "
            "with Togo Mobility."
        )
    )

    # =====================================
    # NOTIFY RIDER
    # =====================================

    send_text(

        booking.selected_rider.phone_no,

        (
            "✅ Ride marked as completed.\n\n"

            "Your payout is being "
            "processed."
        )
    )

    return send_text(

        session.phone_number,

        (
            "Ride completed successfully."
        )
    )
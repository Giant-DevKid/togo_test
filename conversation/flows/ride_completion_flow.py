import re
from rideshare.models import RideBooking

from rideshare.services import generate_ride_otp
from django.utils import timezone


from conversation.services.message_service import send_text

from rideshare.utils.paystack_service import release_rider_payment

from conversation.ai.extractors.ride_completion_extractor import (
    extract_ride_completion_data,
)


def get_active_booking(rider):

    return (
        RideBooking.objects.filter(
            selected_rider=rider, status__in=["CONFIRMED", "IN_PROGRESS", "OTP_PENDING"]
        )
        .order_by("-created_at")
        .first()
    )


def handle_request_otp(session, booking_id=None):

    booking = None

    # =====================================
    # USE PROVIDED BOOKING
    # =====================================

    if booking_id:

        booking = RideBooking.objects.filter(
            # id=booking_id,
            booking_id=booking_id,
            selected_rider=session.user,
        ).first()

    # =====================================
    # AUTO FIND ACTIVE BOOKING
    # =====================================

    else:

        booking = get_active_booking(session.user)

    if not booking:

        return send_text(session.phone_number, ("No active ride found."))

    otp = generate_ride_otp(booking)

    send_text(booking.passenger.phone_no, ("🔐 Ride Completion OTP\n\n" f"OTP: {otp}"))

    return send_text(session.phone_number, ("OTP sent to passenger."))


def handle_verify_otp(session, booking_id=None, otp=None):

    booking = None

    if booking_id:

        booking = RideBooking.objects.filter(
            # id=booking_id,
            booking_id=booking_id,
            selected_rider=session.user,
            status="OTP_PENDING",
        ).first()

    else:

        booking = (
            RideBooking.objects.filter(
                selected_rider=session.user, status="OTP_PENDING"
            )
            .order_by("-created_at")
            .first()
        )

    if not booking:

        return send_text(session.phone_number, ("No OTP pending ride found."))

    if booking.ride_completion_otp != otp:

        return send_text(session.phone_number, "Invalid OTP.")

    booking.status = "COMPLETED"

    booking.otp_verified_at = timezone.now()

    booking.save()

    release_rider_payment(booking)

    send_text(booking.passenger.phone_no, ("✅ Ride completed."))

    send_text(
        booking.selected_rider.phone_no, ("✅ Ride completed.\n\n" "Payout processing.")
    )

    return send_text(session.phone_number, ("Ride completed successfully."))


# def handle_ride_completion_flow(
#     session,
#     message
# ):

#     extracted = (
#         extract_ride_completion_data(
#             message
#         )
#     )

#     action = extracted.get(
#         "action"
#     )

#     booking_id = extracted.get(
#         "booking_id"
#     )

#     otp = extracted.get(
#         "otp"
#     )

#     # =====================================
#     # REQUEST OTP
#     # =====================================

#     if action == "REQUEST_OTP":

#         return handle_request_otp(

#             session,

#             booking_id
#         )

#     # =====================================
#     # VERIFY OTP
#     # =====================================

#     if action == "VERIFY_OTP":

#         return handle_verify_otp(

#             session,

#             booking_id,

#             otp
#         )

#     return send_text(

#         session.phone_number,

#         (
#             "I couldn't understand "
#             "your request."
#         )
#     )


def handle_ride_completion_flow(session, message):

    extracted = extract_ride_completion_data(message)

    action = extracted.get("action")
    booking_id = extracted.get("booking_id")
    otp = extracted.get("otp")

    # =====================================
    # VALIDATE BOOKING ID FORMAT
    # =====================================

    if booking_id and not re.match(r"^RID-[A-Z0-9]{6}$", booking_id):

        return send_text(session.phone_number, "Invalid booking reference.")

    # =====================================
    # REQUEST OTP
    # =====================================

    if action == "REQUEST_OTP":

        return handle_request_otp(session, booking_id)

    # =====================================
    # VERIFY OTP
    # =====================================

    if action == "VERIFY_OTP":

        return handle_verify_otp(session, booking_id, otp)

    return send_text(session.phone_number, "I couldn't understand your request.")

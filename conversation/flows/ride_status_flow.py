from rideshare.models import (
    RideBooking
)

from conversation.services.message_service import (
    send_text, send_image
)

def view_my_rides(session):

    bookings = (

        RideBooking.objects
        .filter(
            passenger=session.user
        )
        .order_by("-created_at")[:10]
    )

    if not bookings:

        return send_text(

            session.phone_number,

            "You do not have any rides yet."
        )

    message = (
        "🚘 Your Active Rides\n\n"
    )

    for booking in bookings:

        message += (

            f"Ride ID: {booking.id}\n"

            f"{booking.pickup_name} → "

            f"{booking.destination_name}\n"

            f"Price: ₦{booking.estimated_price}\n"

            f"Status: {booking.status}\n\n"
        )

    return send_text(

        session.phone_number,

        message
    )
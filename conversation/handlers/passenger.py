from conversation.constants import *

from whatsapp.services import (
    send_whatsapp_message,
    send_interactive_buttons_message
)

from rideshare.models import (
    RideBooking,
    RideBookingResponse,
)
from rideshare.services import (
    geocode_location, get_route, create_booking, find_matching_routes, notify_riders
)




def start_ride_booking(
    session
):

    session.state = (
        ASK_PICKUP_LOCATION
    )

    session.save()

    return send_whatsapp_message(

        session.phone_number,

        "Enter pickup location"
    )


def handle_pickup_location(
    session,
    message
):

    session.context["pickup_name"] = (
        message
    )

    session.state = (
        ASK_DESTINATION_LOCATION
    )

    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "Enter destination"
    )


def handle_destination_location(
    session,
    message
):

    pickup_name = (
        session.context.get(
            "pickup_name"
        )
    )

    destination_name = (
        message.strip()
    )

    # =========================
    # VALIDATE PICKUP
    # =========================
    pickup = geocode_location(
        pickup_name
    )

    if not pickup:

        return send_whatsapp_message(

            session.phone_number,

            (
                "❌ Pickup location not found.\n\n"
                "Please restart booking and enter "
                "a more accurate pickup location.\n\n"
                "Example:\n"
                "Yaba Lagos"
            )
        )

    # =========================
    # VALIDATE DESTINATION
    # =========================
    destination = geocode_location(
        destination_name
    )

    if not destination:

        return send_whatsapp_message(

            session.phone_number,

            (
                "❌ Destination not found.\n\n"
                "Please enter a more accurate "
                "destination.\n\n"
                "Example:\n"
                "Ikeja Lagos"
            )
        )

    # =========================
    # GET ROUTE
    # =========================
    try:

        route_data = get_route(

            pickup["lng"],
            pickup["lat"],

            destination["lng"],
            destination["lat"]
        )

    except Exception as e:

        print("ROUTE ERROR:", str(e))

        return send_whatsapp_message(

            session.phone_number,

            (
                "❌ Unable to generate route.\n\n"
                "Please try again later."
            )
        )

    # =========================
    # CREATE BOOKING
    # =========================
    booking = create_booking(

        passenger=session.user,

        pickup_name=pickup_name,

        destination_name=destination_name,

        pickup=pickup,

        destination=destination,

        route_data=route_data
    )

    # =========================
    # FIND MATCHING RIDERS
    # =========================
    matches = find_matching_routes(

        (
            pickup["lat"],
            pickup["lng"]
        ),

        (
            destination["lat"],
            destination["lng"]
        )
    )

    # =========================
    # NOTIFY RIDERS
    # =========================
    if matches:

        notify_riders(
            booking,
            matches
        )

    session.context["booking_id"] = (
        str(booking.id)
    )

    session.state = SELECT_RIDER

    session.save()

    # =========================
    # RESPONSE
    # =========================
    if not matches:

        return send_whatsapp_message(

            session.phone_number,

            (
                f"🚘 Booking Created\n\n"

                f"From: {pickup_name}\n"
                f"To: {destination_name}\n\n"

                f"Estimated Price: "
                f"₦{booking.estimated_price}\n\n"

                "No riders available yet.\n"
                "Searching for riders..."
            )
        )

    return send_whatsapp_message(

        session.phone_number,

        (
            f"🚘 Booking Created\n\n"

            f"From: {pickup_name}\n"
            f"To: {destination_name}\n\n"

            f"Estimated Price: "
            f"₦{booking.estimated_price}\n\n"

            f"{len(matches)} rider(s) notified.\n"
            "Waiting for rider acceptance..."
        )
    )


def show_passenger_bookings(
    session
):

    bookings = RideBooking.objects.filter(
        passenger=session.user
    ).order_by("-created_at")[:10]

    if not bookings.exists():

        return send_whatsapp_message(

            session.phone_number,

            "No bookings found"
        )

    text = "Your Recent Bookings 🚗\n\n"

    for booking in bookings:

        text += (

            f"Booking ID: {booking.id}\n"

            f"{booking.pickup_location} → "
            f"{booking.destination_location}\n"

            f"Price: ₦{booking.estimated_price}\n"

            f"Status: {booking.status}\n\n"
        )

    return send_whatsapp_message(
        session.phone_number,
        text
    )

def select_rider_handler(
    session,
    message
):

    response_id = (
        message.replace(
            "select_rider_",
            ""
        )
    )

    response = (
        RideBookingResponse.objects
        .select_related(
            "rider"
        )
        .get(id=response_id)
    )

    booking = response.booking

    price = (

        response.updated_price

        or

        booking.estimated_price
    )

    session.context[
        "selected_response_id"
    ] = response.id

    session.save()

    body = (

        f"Booking ID: "
        f"{booking.id}\n\n"

        f"Rider: "
        f"{response.rider.first_name}\n"

        f"Price: ₦{price}\n\n"

        "Proceed with booking?"
    )

    buttons = [

        {
            "id":
                f"proceed_payment_"
                f"{booking.id}",

            "title":
                "Proceed"
        },

        {
            "id":
                f"cancel_booking_"
                f"{booking.id}",

            "title":
                "Cancel"
        }
    ]

    return send_interactive_buttons_message(

        to=session.phone_number,

        body=body,

        buttons=buttons
    )

def handle_select_rider(
    session,
    message
):

    if ":" not in message:

        return send_whatsapp_message(
            session.phone_number,
            "Invalid selection"
        )

    _, response_id = message.split(":")

    response = RideBookingResponse.objects.filter(
        id=response_id
    ).select_related(
        "rider",
        "booking"
    ).first()

    if not response:

        return send_whatsapp_message(
            session.phone_number,
            "Rider not found"
        )

    rider = response.rider

    booking = response.booking

    vehicle = getattr(
        rider,
        "vehicles",
        None
    )

    plate_no = (
        vehicle.plate_no
        if vehicle
        else "N/A"
    )

    buttons = [

        {
            "id":
                f"proceed_payment:{booking.id}",

            "title":
                "Proceed Pay",
        },

        {
            "id":
                f"cancel_booking:{booking.id}",

            "title":
                "Cancel",
        }
    ]

    return send_interactive_buttons_message(

        to=session.phone_number,

        body=(

            f"Booking ID: {booking.id}\n\n"

            f"Rider: {rider.first_name}\n"

            f"Vehicle Plate: {plate_no}\n"

            f"Price: ₦{response.updated_price or booking.estimated_price}"
        ),

        buttons=buttons,
    )


def proceed_to_payment_handler(
    session,
    booking_id
):

    booking = RideBooking.objects.filter(
        id=booking_id
    ).first()

    if not booking:

        return send_whatsapp_message(
            session.phone_number,
            "Booking not found"
        )

    booking.status = "PENDING_PAYMENT"

    booking.save()

    return send_whatsapp_message(

        session.phone_number,

        (
            f"Proceeding to payment for "
            f"Booking #{booking.id}"
        )
    )

def cancel_booking_handler(
    session,
    booking_id
):

    booking = RideBooking.objects.filter(
        id=booking_id
    ).first()

    if not booking:

        return send_whatsapp_message(
            session.phone_number,
            "Booking not found"
        )

    booking.status = "CANCELLED"

    booking.save()

    return send_whatsapp_message(

        session.phone_number,

        "Booking cancelled successfully"
    )

def handle_confirm_booking(
    session,
    message
):

    return send_whatsapp_message(

        session.phone_number,

        "Booking confirmed"
    )


def passenger_select_rider_handler(
    session,
    response_id
):

    response = RideBookingResponse.objects.get(
        id=response_id
    )

    booking = response.booking

    session.context["selected_response"] = (
        response.id
    )

    session.save()

    buttons = [

        {
            "id":
                f"proceed_payment_{booking.id}",

            "title":
                "Proceed Payment"
        },

        {
            "id":
                f"cancel_booking_{booking.id}",

            "title":
                "Cancel Booking"
        },
    ]

    return send_interactive_buttons_message(

        to=session.phone_number,

        body=(

            f"Booking ID: "
            f"{booking.id}\n\n"

            f"Driver: "
            f"{response.rider.first_name}\n"

            f"Vehicle: "
            f"{response.rider.vehicles.brand}\n"

            f"Plate: "
            f"{response.rider.vehicles.plate_no}\n"

            f"Price: "
            f"₦{response.updated_price}"
        ),

        buttons=buttons,
    )



def proceed_payment_handler(
    session,
    booking_id
):

    booking = RideBooking.objects.filter(
        id=booking_id,
        passenger=session.user
    ).first()

    if not booking:

        return send_whatsapp_message(

            session.phone_number,

            "Booking not found"
        )

    booking.status = "PAYMENT_PENDING"

    booking.save()

    return send_whatsapp_message(

        session.phone_number,

        (
            "Payment processing will "
            "be integrated soon 💳\n\n"

            f"Booking ID: {booking.id}"
        )
    )


def cancel_booking_handler(
    session,
    booking_id
):

    booking = RideBooking.objects.filter(
        id=booking_id,
        passenger=session.user
    ).first()

    if not booking:

        return send_whatsapp_message(

            session.phone_number,

            "Booking not found"
        )

    booking.status = "CANCELLED"

    booking.save()

    return send_whatsapp_message(

        session.phone_number,

        "Booking cancelled successfully ❌"
    )
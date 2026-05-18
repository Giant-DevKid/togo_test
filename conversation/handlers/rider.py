from rideshare.models import (
    Vehicle,
    RideBooking,
    RideBookingResponse,
    DriverRoute,

    )

from rideshare.services import (
    get_user_vehicle,
    create_driver_route,
    notify_passenger_of_responses,
)
from whatsapp.services import (
    send_whatsapp_buttons,
    send_whatsapp_message,
    send_interactive_buttons_message
)

from conversation.constants import *

from conversation.handlers.onboarding import (
    show_main_menu
)

from conversation.submenu_config.rider_profile_menu import (
    RIDER_PROFILE_MENU as RIDER_PROFILE_BUTTONS
)

from conversation.submenu_config.route_menu import (
    ROUTE_MENU
)
from decimal import Decimal


from rideshare.services import (
    notify_passenger_of_booking_update
)


def rider_profile_menu_handler(session):

    session.state = RIDER_PROFILE_MENU

    session.save()

    return send_whatsapp_buttons(
        to=session.phone_number,
        body_text="Profile Menu",
        buttons=RIDER_PROFILE_BUTTONS
    )

def my_profile_handler(session):

    user = session.user

    return send_whatsapp_message(
        session.phone_number,
        (
            f"👤 My Profile\n\n"
            f"Name: {user.first_name} "
            f"{user.last_name}\n"
            f"Email: {user.email}\n"
            f"Phone: {user.phone_no}"
        )
    )

def route_profile_handler(session):

    return send_whatsapp_message(
        session.phone_number,
        (
            "🛣 Route Profile\n\n"
            "No route configured yet."
        )
    )


def ride_orders_handler(session):

    return send_whatsapp_message(
        session.phone_number,
        (
            "📦 Orders\n\n"
            "No ride orders yet."
        )
    )

def vehicle_profile_handler(session):

    vehicle = get_user_vehicle(
        session.user
    )

    if not vehicle:

        return send_whatsapp_buttons(
            to=session.phone_number,
            body_text=(
                "No vehicle profile found"
            ),
            buttons=[
                {
                    "id": "add_vehicle",
                    "title": "Add Vehicle"
                },
                {
                    "id": "go_back_main_menu",
                    "title": "Go Back"
                }
            ]
        )

    return send_whatsapp_buttons(
        to=session.phone_number,
        body_text=(
            f"🚘 Vehicle Info\n\n"
            f"Type: {vehicle.type}\n"
            f"Brand: {vehicle.brand}\n"
            f"Plate No: {vehicle.plate_no}\n"
            f"Seat Capacity: "
            f"{vehicle.seat_cap}"
        ),
        buttons=[
            {
                "id": "update_vehicle",
                "title": "Update"
            },
            {
                "id": "go_back_main_menu",
                "title": "Go Back"
            }
        ]
    )

def add_vehicle_handler(session):

    session.state = ASK_VEHICLE_TYPE

    session.context["vehicle_action"] = (
        "create"
    )

    session.save()

    return send_whatsapp_buttons(
        to=session.phone_number,
        body_text="Select vehicle type",
        buttons=[
            {
                "id": "Car",
                "title": "Car"
            },
            {
                "id": "Bus",
                "title": "Bus"
            },
            {
                "id": "Motorcycle",
                "title": "Bike"
            }
        ]
    )


def update_vehicle_handler(session):

    session.state = ASK_VEHICLE_TYPE

    session.context["vehicle_action"] = (
        "update"
    )

    session.save()

    return send_whatsapp_buttons(
        to=session.phone_number,
        body_text="Update vehicle type",
        buttons=[
            {
                "id": "Car",
                "title": "Car"
            },
            {
                "id": "Bus",
                "title": "Bus"
            },
            {
                "id": "Motorcycle",
                "title": "Bike"
            }
        ]
    )


# ==========================================
# Vehicle Conversation Flow Handlers
# ==========================================

def handle_vehicle_type(
    session,
    message
):

    session.context["vehicle_type"] = (
        message
    )

    session.state = ASK_VEHICLE_BRAND

    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "Enter vehicle brand"
    )


def handle_vehicle_brand(
    session,
    message
):

    session.context["vehicle_brand"] = (
        message
    )

    session.state = ASK_VEHICLE_PLATE_NO

    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "Enter plate number"
    )


def handle_vehicle_plate_no(
    session,
    message
):

    session.context["vehicle_plate_no"] = (
        message
    )

    session.state = ASK_VEHICLE_SEAT_CAP

    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "Enter seat capacity"
    )


def handle_vehicle_seat_cap(
    session,
    message
):

    vehicle, created = (
        Vehicle.objects.get_or_create(
            user=session.user
        )
    )

    vehicle.type = (
        session.context["vehicle_type"]
    )

    vehicle.brand = (
        session.context["vehicle_brand"]
    )

    vehicle.plate_no = (
        session.context["vehicle_plate_no"]
    )

    vehicle.seat_cap = int(message)

    vehicle.save()

    session.state = MAIN_MENU

    session.save()

    send_whatsapp_message(
        session.phone_number,
        (
            "Vehicle profile saved "
            "successfully ✅"
        )
    )
    return show_main_menu(session)


def route_profile_handler(session):

    session.state = RIDER_ROUTE_MENU

    session.save()

    return send_interactive_buttons_message(

        to=session.phone_number,

        body="Route Menu",

        buttons=ROUTE_MENU,
    )


def create_route_handler(session):

    session.state = ASK_ROUTE_START

    session.save()

    return send_whatsapp_message(

        session.phone_number,

        "Enter route starting location"
    )


def handle_route_start(
    session,
    message
):

    session.context["route_start"] = (
        message
    )

    session.state = ASK_ROUTE_DESTINATION

    session.save()

    return send_whatsapp_message(

        session.phone_number,

        "Enter destination location"
    )


def handle_route_destination(
    session,
    message
):

    route_start = session.context.get(
        "route_start"
    )

    route_destination = message

    route = create_driver_route(

        driver=session.user,

        start_name=route_start,

        end_name=route_destination,
    )

    session.state = RIDER_ROUTE_MENU

    session.save()

    return send_whatsapp_message(

        session.phone_number,

        (
            "Route created successfully ✅\n\n"

            f"{route.start_name} → "
            f"{route.end_name}"
        )
    )


def my_routes_handler(session):

    routes = DriverRoute.objects.filter(
        driver=session.user
    ).order_by("-created_at")

    if not routes.exists():

        return send_whatsapp_message(

            session.phone_number,

            "No routes found"
        )

    text = "Your Routes 🚗\n\n"

    for route in routes:

        text += (

            f"{route.start_name} → "
            f"{route.end_name}\n\n"
        )

    return send_whatsapp_message(
        session.phone_number,
        text
    )



def rider_accept_booking_handler(
    session,
    booking_id
):

    booking = RideBooking.objects.get(
        id=booking_id
    )

    route = booking.matched_routes.filter(
        driver=session.user
    ).first()

    RideBookingResponse.objects.update_or_create(

        booking=booking,

        rider=session.user,

        defaults={

            "route": route,

            "response": "ACCEPTED",

            "updated_price":
                booking.estimated_price,
        }
    )

    notify_passenger_of_booking_update(
        booking
    )

    return send_whatsapp_message(

        session.phone_number,

        "Ride accepted successfully ✅"
    )


def rider_reject_booking_handler(
    session,
    booking_id
):

    booking = RideBooking.objects.get(
        id=booking_id
    )

    route = booking.matched_routes.filter(
        driver=session.user
    ).first()

    RideBookingResponse.objects.update_or_create(

        booking=booking,

        rider=session.user,

        defaults={

            "route": route,

            "response": "REJECTED",
        }
    )

    return send_whatsapp_message(

        session.phone_number,

        "Ride rejected"
    )


def rider_change_price_handler(
    session,
    booking_id
):

    session.context["booking_id"] = (
        booking_id
    )

    session.state = ASK_NEW_BOOKING_PRICE

    session.save()

    return send_whatsapp_message(

        session.phone_number,

        "Enter your new booking price"
    )


def handle_new_booking_price(
    session,
    message
):

    booking_id = session.context.get(
        "booking_id"
    )

    booking = RideBooking.objects.get(
        id=booking_id
    )

    route = booking.matched_routes.filter(
        driver=session.user
    ).first()

    new_price = Decimal(message)

    RideBookingResponse.objects.update_or_create(

        booking=booking,

        rider=session.user,

        defaults={

            "route": route,

            "response": "PRICE_UPDATED",

            "updated_price": new_price,
        }
    )

    notify_passenger_of_booking_update(
        booking
    )

    session.state = MAIN_MENU

    session.save()

    return send_whatsapp_message(

        session.phone_number,

        "Price updated successfully ✅"
    )
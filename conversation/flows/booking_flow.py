from conversation.ai.extractors.booking_extractor import extract_booking_data

from conversation.ai.extractors.update_extractor import extract_update_data

from conversation.services.message_service import send_text

from conversation.services.session_service import reset_session

from conversation.state.booking_steps import (
    BOOKING_FLOW,
    AWAITING_PICKUP,
    AWAITING_DESTINATION,
)

from rideshare.models import RideBooking

from rideshare.services import (
    geocode_location,
    get_route,
    create_booking,
    find_matching_routes,
    notify_riders,
)


# =========================================
# UPDATE BOOKING
# =========================================
def update_booking_flow(session, message):

    extracted = extract_update_data(message)

    booking = (
        RideBooking.objects.filter(passenger=session.user, status="PENDING")
        .order_by("-created_at")
        .first()
    )

    if not booking:

        return send_text(session.phone_number, "No active booking found")

    pickup_name = extracted.get("pickup_name")

    destination_name = extracted.get("destination_name")

    if pickup_name:

        pickup = geocode_location(pickup_name)

        booking.pickup_name = pickup_name
        booking.pickup_lat = pickup["lat"]
        booking.pickup_lng = pickup["lng"]

    else:

        pickup = {"lat": booking.pickup_lat, "lng": booking.pickup_lng}

    if destination_name:

        destination = geocode_location(destination_name)

        booking.destination_name = destination_name

        booking.destination_lat = destination["lat"]

        booking.destination_lng = destination["lng"]

    else:

        destination = {"lat": booking.destination_lat, "lng": booking.destination_lng}

    route_data = get_route(
        pickup["lng"], pickup["lat"], destination["lng"], destination["lat"]
    )

    booking.distance_meters = route_data["distance"]

    booking.route_geometry = route_data["geometry"]

    booking.encoded_polyline = route_data["geometry"]

    booking.save()

    return send_text(
        session.phone_number,
        (
            "Ride updated successfully ✅\n\n"
            f"Pickup: "
            f"{booking.pickup_name}\n"
            f"Destination: "
            f"{booking.destination_name}"
        ),
    )


# =========================================
# CANCEL BOOKING
# =========================================
def cancel_booking_flow(session):

    booking = (
        RideBooking.objects.filter(
            passenger=session.user,
            status__in=[
                "PENDING",
                "RIDER_SELECTED",
                "PAYMENT_PENDING",
                "CONFIRMED",
                "IN_PROGRESS",
                "OTP_PENDING",
            ],
        )
        .order_by("-created_at")
        .first()
    )

    if not booking:

        return send_text(session.phone_number, "No active booking found")

    booking.status = "CANCELLED"

    booking.save()

    reset_session(session)

    return send_text(session.phone_number, "Booking cancelled successfully ❌")


# =========================================
# MAIN BOOKING FLOW
# =========================================
def handle_booking_flow(session, message, intent):

    active_flow = session.context.get("active_flow")

    step = session.context.get("step")

    # =====================================
    # CONTINUE ACTIVE FLOW
    # =====================================

    if active_flow == BOOKING_FLOW:

        if step == AWAITING_PICKUP:

            return handle_pickup_step(session, message)

        if step == AWAITING_DESTINATION:

            return handle_destination_step(session, message)

    # =====================================
    # NEW BOOKING
    # =====================================

    if intent == "BOOK_RIDE":

        return start_booking_flow(session, message)

    # =====================================
    # UPDATE BOOKING
    # =====================================

    if intent == "UPDATE_BOOKING":

        return update_booking_flow(session, message)

    # =====================================
    # CANCEL BOOKING
    # =====================================

    if intent == "CANCEL_BOOKING":

        return cancel_booking_flow(session)


# =========================================
# START BOOKING FLOW
# =========================================
def start_booking_flow(session, message):

    extracted = extract_booking_data(message)

    pickup_name = extracted.get("pickup_name")

    destination_name = extracted.get("destination_name")

    # =====================================
    # ASK PICKUP
    # =====================================

    if not pickup_name:

        session.context = {
            "active_flow": BOOKING_FLOW,
            "step": AWAITING_PICKUP,
            "data": {},
        }

        session.save()

        return send_text(session.phone_number, "📍 Where should we pick you up?")

    # =====================================
    # ASK DESTINATION
    # =====================================

    if not destination_name:

        session.context = {
            "active_flow": BOOKING_FLOW,
            "step": AWAITING_DESTINATION,
            "data": {"pickup_name": pickup_name},
        }

        session.save()

        return send_text(session.phone_number, "📍 Where are you going?")

    return create_booking_flow(session, pickup_name, destination_name)


# =========================================
# HANDLE PICKUP STEP
# =========================================
def handle_pickup_step(session, message):

    pickup_name = message.strip()

    # =====================================
    # VALIDATE PICKUP
    # =====================================

    pickup = geocode_location(pickup_name)

    if not pickup:

        return send_text(
            session.phone_number,
            (
                "❌ Pickup location not found.\n\n"
                "Please enter a more accurate "
                "pickup location.\n\n"
                "Example:\n"
                "Yaba Lagos"
            ),
        )

    session.context = {
        "active_flow": BOOKING_FLOW,
        "step": AWAITING_DESTINATION,
        "data": {"pickup_name": pickup_name},
    }

    session.save()

    return send_text(session.phone_number, "📍 Where are you going?")


# =========================================
# HANDLE DESTINATION STEP
# =========================================
def handle_destination_step(session, message):

    pickup_name = session.context["data"].get("pickup_name")

    destination_name = message.strip()

    # =====================================
    # VALIDATE DESTINATION
    # =====================================

    destination = geocode_location(destination_name)

    if not destination:

        return send_text(
            session.phone_number,
            (
                "❌ Destination location "
                "not found.\n\n"
                "Please enter a more accurate "
                "destination.\n\n"
                "Example:\n"
                "Ikeja Lagos"
            ),
        )

    return create_booking_flow(session, pickup_name, destination_name)


# =========================================
# CREATE BOOKING
# =========================================
def create_booking_flow(session, pickup_name, destination_name):

    pickup = geocode_location(pickup_name)

    destination = geocode_location(destination_name)

    # =====================================
    # SAFETY VALIDATION
    # =====================================

    if not pickup:

        session.context = {
            "active_flow": BOOKING_FLOW,
            "step": AWAITING_PICKUP,
            "data": {},
        }

        session.save()

        return send_text(session.phone_number, "Pickup location not found.")

    if not destination:

        session.context = {
            "active_flow": BOOKING_FLOW,
            "step": AWAITING_DESTINATION,
            "data": {"pickup_name": pickup_name},
        }

        session.save()

        return send_text(session.phone_number, "Destination location not found.")

    # =====================================
    # GET ROUTE
    # =====================================

    route_data = get_route(
        pickup["lng"], pickup["lat"], destination["lng"], destination["lat"]
    )

    # =====================================
    # CHECK EXISTING ACTIVE BOOKING
    # =====================================

    existing_booking = (
        RideBooking.objects.filter(
            passenger=session.user,
            status__in=[
                "PENDING",
                "RIDER_SELECTED",
                "PAYMENT_PENDING",
                "CONFIRMED",
                "IN_PROGRESS",
                "OTP_PENDING",
            ],
        )
        .order_by("-created_at")
        .first()
    )

    if existing_booking:

        reset_session(session)

        return send_text(
            session.phone_number,
            (
                "❌ You already have an active ride booking.\n\n"
                f"Booking ID: {existing_booking.booking_id}\n"
                f"Status: {existing_booking.status}\n\n"
                "You must complete or cancel the current ride "
                "before creating another booking."
            ),
        )

    # =====================================
    # CREATE BOOKING
    # =====================================

    booking = create_booking(
        passenger=session.user,
        pickup_name=pickup_name,
        destination_name=destination_name,
        pickup=pickup,
        destination=destination,
        route_data=route_data,
    )

    # =====================================
    # FIND RIDERS
    # =====================================

    matches = find_matching_routes(
        (pickup["lat"], pickup["lng"]), (destination["lat"], destination["lng"])
    )

    # =====================================
    # NOTIFY RIDERS
    # =====================================

    if matches:

        notify_riders(booking, matches)

    # =====================================
    # RESET FLOW
    # =====================================

    reset_session(session)

    # =====================================
    # SUCCESS MESSAGE
    # =====================================

    send_text(
        session.phone_number,
        (
            f"🚘 Ride booked successfully\n\n"
            f"Bookimg ID: {booking.booking_id}\n"
            f"From: {pickup_name}\n"
            f"To: {destination_name}\n\n"
            f"Estimated Price: "
            # f"₦{booking.estimated_price}"
            f"₦{booking.get_total_price()}"
        ),
    )

    # =====================================
    # STATUS HINT
    # =====================================

    return send_text(
        session.phone_number,
        (
            "You can say:\n\n"
            "• view my rides\n"
            "• check ride status\n"
            "• cancel my ride"
        ),
    )

import re

from rideshare.models import (
    RideBookingResponse,
    RideBooking,
)

from conversation.services.message_service import (
    send_text
)

from conversation.state.rider_request_steps import (

    RIDE_OFFER_FLOW,

    SELECTING_RIDER
)

from conversation.state.payment_steps import *

# =========================================
# VIEW MATCHING REQUESTS
# =========================================
def view_ride_requests(
    session
):

    requests = (

        RideBookingResponse.objects
        .filter(

            rider=session.user,

            response="PENDING"
        )
        .select_related(
            "booking",
            "route"
        )
        .order_by("-created_at")
    )

    if not requests.exists():

        return send_text(

            session.phone_number,

            (
                "You do not have any "
                "pending ride requests."
            )
        )

    message = (
        "🚘 Matching Ride Requests\n\n"
    )

    for index, req in enumerate(
        requests,
        start=1
    ):

        booking = req.booking

        message += (

            f"{index}. "

            f"{booking.pickup_name} → "

            f"{booking.destination_name}\n"

            f"Price: ₦"
            f"{booking.estimated_price}\n"

            f"Request ID: {req.id}\n\n"
        )

    message += (

        "You can say:\n\n"

        "• accept 14\n"

        "• reject 14\n"

        "• offer 14 5000"
    )

    return send_text(

        session.phone_number,

        message
    )


# =========================================
# RIDER RIDE REQUEST ACTIONS SELECTION
# =========================================
def accept_ride_request(
    session,
    response_id
):

    ride_response = (

        RideBookingResponse.objects
        .filter(

            id=response_id,

            rider=session.user
        )
        .select_related("booking")
        .first()
    )

    if not ride_response:

        return send_text(

            session.phone_number,

            (
                "Ride request not found."
            )
        )

    # =====================================
    # UPDATE RESPONSE ONLY
    # =====================================

    ride_response.response = (
        "ACCEPTED"
    )

    ride_response.updated_price = (
        ride_response.booking.estimated_price
    )

    ride_response.save()

    booking = ride_response.booking

    # =====================================
    # NOTIFY PASSENGER
    # =====================================

    send_text(

        booking.passenger.phone_no,

        (
            "🚘 A Driver Accepted Your Ride\n\n"

            f"Driver: "
            f"{session.user.first_name}\n"

            f"Price: ₦"
            f"{booking.estimated_price}\n\n"

            "Say:\n"
            "• view ride offers"
        )
    )

    return send_text(

        session.phone_number,

        "Ride request accepted ✅"
    )


def reject_ride_request(
    session,
    response_id
):

    ride_response = (

        RideBookingResponse.objects
        .filter(

            id=response_id,

            rider=session.user,

            response="PENDING"
        )
        .first()
    )

    if not ride_response:

        return send_text(

            session.phone_number,

            "Ride request not found."
        )

    ride_response.response = (
        "REJECTED"
    )

    ride_response.save()

    return send_text(

        session.phone_number,

        "Ride request rejected."
    )


def offer_new_price(
    session,
    response_id,
    price
):

    ride_response = (

        RideBookingResponse.objects
        .filter(

            id=response_id,

            rider=session.user
        )
        .select_related("booking")
        .first()
    )

    if not ride_response:

        return send_text(

            session.phone_number,

            "Ride request not found."
        )

    # =====================================
    # UPDATE RESPONSE
    # =====================================

    ride_response.response = (
        "ACCEPTED"
    )

    ride_response.updated_price = (
        price
    )

    ride_response.save()

    booking = ride_response.booking

    # =====================================
    # NOTIFY PASSENGER
    # =====================================

    send_text(

        booking.passenger.phone_no,

        (
            "🚘 Driver Sent New Offer\n\n"

            f"Driver: "
            f"{session.user.first_name}\n"

            f"New Price: ₦{price}\n\n"

            "Say:\n"
            "• view ride offers"
        )
    )

    return send_text(

        session.phone_number,

        (
            f"New offer sent: ₦{price} ✅"
        )
    )


# =========================================
# HANDLE DRIVER REQUEST ACTIONS
# =========================================
def handle_driver_request_action(
    session,
    message
):

    normalized_message = (
        message.strip().lower()
    )

    # =====================================
    # ACCEPT
    # accept 14
    # =====================================

    accept_match = re.match(
        r"^accept\s+(\d+)$",
        normalized_message
    )

    if accept_match:

        response_id = int(
            accept_match.group(1)
        )

        return accept_ride_request(

            session,

            response_id
        )

    # =====================================
    # REJECT
    # 
    # =====================================

    reject_match = re.match(
        r"^reject\s+(\d+)$",
        normalized_message
    )

    if reject_match:

        response_id = int(
            reject_match.group(1)
        )

        return reject_ride_request(

            session,

            response_id
        )

    # =====================================
    # OFFER
    #
    # =====================================

    offer_match = re.match(
        r"^offer\s+(\d+)\s+(\d+)$",
        normalized_message
    )

    if offer_match:

        response_id = int(
            offer_match.group(1)
        )

        updated_price = int(
            offer_match.group(2)
        )

        return offer_new_price(

            session,

            response_id,

            updated_price
        )

    return None


# =========================================
# VIEW RIDE OFFERS
# =========================================

def view_ride_offers(
    session
):

    booking = (

        RideBooking.objects
        .filter(

            passenger=session.user,

            status="PENDING"
        )
        .order_by("-created_at")
        .first()
    )

    if not booking:

        return send_text(

            session.phone_number,

            (
                "You do not have any "
                "active ride requests."
            )
        )

    responses = (

        RideBookingResponse.objects
        .filter(

            booking=booking,

            response="ACCEPTED"
        )
        .select_related("rider")
        .order_by("created_at")
    )

    if not responses.exists():

        return send_text(

            session.phone_number,

            (
                "No drivers have responded "
                "to your ride yet."
            )
        )

    message = (
        "🚘 Driver Offers\n\n"
    )

    for index, response in enumerate(
        responses,
        start=1
    ):

        price = (

            response.updated_price

            or

            booking.estimated_price
        )

        message += (

            f"{index}. "

            f"{response.rider.first_name}\n"

            f"Price: ₦{price}\n\n"
        )

    # message += (

    #     "Reply with:\n\n"

    #     "select 1\n"

    #     "select 2"
    # )
    message += (

        "Reply with the number of "
        "the driver you want.\n\n"

        "Example:\n"
        "1"
    )

    # =====================================
    # SAVE FLOW CONTEXT
    # =====================================

    session.context = {

        "active_flow": (
            RIDE_OFFER_FLOW
        ),

        "step": (
            SELECTING_RIDER
        ),

        "data": {

            "booking_id": booking.id
        }
    }

    session.save()

    return send_text(

        session.phone_number,

        message
    )


# =========================================
# HANDLE RIDER SELECTION
# =========================================
def handle_rider_selection(
    session,
    message
):

    normalized_message = (
        message.strip()
    )

    # =====================================
    # VALIDATE INPUT
    # =====================================

    if not normalized_message.isdigit():

        return send_text(

            session.phone_number,

            (
                "Please reply with the "
                "driver number only.\n\n"

                "Example:\n"
                "1"
            )
        )

    selected_index = int(
        normalized_message
    )

    # =====================================
    # GET BOOKING
    # =====================================

    booking_id = (

        session.context["data"]
        .get("booking_id")
    )

    booking = (

        RideBooking.objects
        .filter(

            id=booking_id,

            passenger=session.user
        )
        .first()
    )

    if not booking:

        return send_text(

            session.phone_number,

            "Booking not found."
        )

    # =====================================
    # GET ACCEPTED RESPONSES
    # =====================================

    responses = list(

        RideBookingResponse.objects
        .filter(

            booking=booking,

            response="ACCEPTED"
        )
        .select_related("rider")
        .order_by("created_at")
    )

    if not responses:

        return send_text(

            session.phone_number,

            (
                "No accepted driver offers found."
            )
        )

    # =====================================
    # VALIDATE SELECTION
    # =====================================

    if (

        selected_index < 1

        or

        selected_index > len(responses)
    ):

        return send_text(

            session.phone_number,

            (
                "Invalid driver number.\n\n"

                "Please choose a valid "
                "number from the list."
            )
        )

    selected_response = responses[
        selected_index - 1
    ]

    # =====================================
    # FINALIZE BOOKING
    # =====================================

    booking.selected_rider = (
        selected_response.rider
    )

    booking.final_price = (

        selected_response.updated_price

        or

        booking.estimated_price
    )

    booking.status = (
        "PAYMENT_PENDING"
    )

    booking.save()
    session.context = {

        "active_flow": PAYMENT_FLOW,

        "step": AWAITING_PAYMENT,

        "data": {

            "booking_id": booking.id
        }
    }

    session.save()

    # =====================================
    # CANCEL OTHER RESPONSES
    # =====================================

    RideBookingResponse.objects.filter(

        booking=booking

    ).exclude(

        id=selected_response.id

    ).update(
        response="CANCELLED"
    )

    # =====================================
    # NOTIFY SELECTED DRIVER
    # =====================================

    send_text(

        selected_response.rider.phone_no,

        (
            "🎉 Passenger Selected You\n\n"

            f"Pickup: "
            f"{booking.pickup_name}\n"

            f"Destination: "
            f"{booking.destination_name}\n\n"

            f"Final Price: "
            f"₦{booking.final_price}"
        )
    )

    session.save()

    return send_text(

        session.phone_number,

       
        (
            "✅ Driver selected successfully\n\n"

            f"Driver: "
            f"{selected_response.rider.first_name}\n"

            f"Price: ₦{booking.final_price}\n\n"

            "Reply with:\n\n"

            "• pay now\n"

            "• cancel ride"
        )
    )



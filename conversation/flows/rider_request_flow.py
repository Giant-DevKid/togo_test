import re

from rideshare.models import (
    RideBookingResponse
)

from conversation.services.message_service import (
    send_text
)


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
# ACCEPT RIDE REQUEST
# =========================================
def accept_ride_request(
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
        .select_related("booking")
        .first()
    )

    if not ride_response:

        return send_text(

            session.phone_number,

            (
                "Ride request not found "
                "or already handled."
            )
        )

    # =====================================
    # ACCEPT RESPONSE
    # =====================================

    ride_response.response = (
        "ACCEPTED"
    )

    ride_response.save()

    booking = ride_response.booking

    # =====================================
    # UPDATE BOOKING
    # =====================================

    booking.selected_rider = (
        session.user
    )

    booking.status = (
        "RIDER_SELECTED"
    )

    booking.final_price = (
        booking.estimated_price
    )

    booking.save()

    # =====================================
    # CANCEL OTHER REQUESTS
    # =====================================

    RideBookingResponse.objects.filter(

        booking=booking

    ).exclude(

        id=ride_response.id

    ).update(
        response="CANCELLED"
    )

    # =====================================
    # NOTIFY PASSENGER
    # =====================================

    send_text(

        booking.passenger.phone_no,

        (
            "✅ Rider Accepted Your Ride\n\n"

            f"Driver: "
            f"{session.user.first_name}\n"

            f"Price: ₦"
            f"{booking.final_price}\n\n"

            "You can say:\n"

            "• view my rides"
        )
    )

    return send_text(

        session.phone_number,

        (
            "Ride request accepted ✅"
        )
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
        "CANCELLED"
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

            rider=session.user,

            response="PENDING"
        )
        .select_related("booking")
        .first()
    )

    if not ride_response:

        return send_text(

            session.phone_number,

            "Ride request not found or already processed."
        )

    ride_response.response = (
        "ACCEPTED"
    )

    ride_response.updated_price = (
        price
    )

    ride_response.save()

    booking = ride_response.booking

    booking.selected_rider = (
        session.user
    )

    booking.final_price = price

    booking.status = (
        "RIDER_SELECTED"
    )

    booking.save()

    # cancel others
    RideBookingResponse.objects.filter(

        booking=booking

    ).exclude(

        id=ride_response.id

    ).update(
        response="CANCELLED"
    )

    # notify passenger
    send_text(

        booking.passenger.phone_no,

        (
            "🚘 Rider Accepted Your Ride\n\n"

            f"New Price: ₦{price}\n\n"

            f"Driver: "
            f"{session.user.first_name}"
        )
    )

    return send_text(

        session.phone_number,

        (
            "Ride accepted with "
            f"new price ₦{price} ✅"
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
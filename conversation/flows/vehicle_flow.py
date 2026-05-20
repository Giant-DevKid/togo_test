from rideshare.models import Vehicle

from rideshare.services import get_user_vehicle

from conversation.services.message_service import send_text, send_buttons

from conversation.state.vehicle_steps import (
    VEHICLE_FLOW,
    ASK_VEHICLE_TYPE,
    ASK_VEHICLE_BRAND,
    ASK_VEHICLE_PLATE_NO,
    ASK_VEHICLE_SEAT_CAP,
)

from conversation.services.session_service import reset_session

VALID_VEHICLE_TYPES = ["Car", "Bus", "Motorcycle"]


# =========================================
# MAIN FLOW
# =========================================
def handle_vehicle_flow(session, message, intent):

    step = session.context.get("step")

    # =====================================
    # CONTINUE FLOW
    # =====================================

    if step == ASK_VEHICLE_TYPE:

        return handle_vehicle_type_step(session, message)

    if step == ASK_VEHICLE_BRAND:

        return handle_vehicle_brand_step(session, message)

    if step == ASK_VEHICLE_PLATE_NO:

        return handle_vehicle_plate_step(session, message)

    if step == ASK_VEHICLE_SEAT_CAP:

        return handle_vehicle_seat_cap_step(session, message)

    # =====================================
    # NEW FLOW
    # =====================================

    if intent == "VIEW_VEHICLE":

        return view_vehicle_flow(session)

    if intent == "CREATE_VEHICLE":

        return start_vehicle_flow(session, action="create")

    if intent == "UPDATE_VEHICLE":

        return start_vehicle_flow(session, action="update")


# =========================================
# VIEW VEHICLE
# =========================================
def view_vehicle_flow(session):

    vehicle = get_user_vehicle(session.user)

    if not vehicle:
        return send_buttons(
            session.phone_number,
            ("You don't have a " "vehicle profile yet."),
            [{"id": "create vehicle", "title": "Add Vehicle"}],
        )

    return send_buttons(
        session.phone_number,
        (
            f"🚘 Vehicle Profile\n\n"
            f"Type: {vehicle.type}\n"
            f"Brand: {vehicle.brand}\n"
            f"Plate Number: "
            f"{vehicle.plate_no}\n"
            f"Seat Capacity: "
            f"{vehicle.seat_cap}\n\n"
        ),
        [
            {"id": "update_my_vehicle", "title": "Update my vehicle"},
        ],
    )


# =========================================
# START FLOW
# =========================================
def start_vehicle_flow(session, action):

    session.context = {
        "active_flow": VEHICLE_FLOW,
        "step": ASK_VEHICLE_TYPE,
        "data": {"vehicle_action": action},
    }

    session.save()
    return send_buttons(
        session.phone_number,
        ("What type of vehicle " "do you have?"),
        [
            {"id": "car", "title": "Car"},
            {"id": "bus", "title": "Bus"},
            {"id": "motorcycle", "title": "Motorcycle"},
        ],
    )


# =========================================
# VEHICLE TYPE
# =========================================
def handle_vehicle_type_step(session, message):

    raw = message.strip().lower()

    valid_types = {
        "car": "Car",
        "bus": "Bus",
        "motorcycle": "Motorcycle",
        "bike": "Motorcycle",
    }

    vehicle_type = valid_types.get(raw)

    if not vehicle_type:
        return send_buttons(
            session.phone_number,
            ("Invalid vehicle type. " "Please click on the button to proceed?"),
            [
                {"id": "car", "title": "Car"},
                {"id": "bus", "title": "Bus"},
                {"id": "motorcycle", "title": "Motorcycle"},
            ],
        )

    session.context["data"]["vehicle_type"] = vehicle_type

    session.context["step"] = ASK_VEHICLE_BRAND

    session.save()

    return send_text(session.phone_number, "What is the vehicle brand?")


# =========================================
# VEHICLE BRAND
# =========================================
def handle_vehicle_brand_step(session, message):

    session.context["data"]["vehicle_brand"] = message.strip()

    session.context["step"] = ASK_VEHICLE_PLATE_NO

    session.save()

    return send_text(session.phone_number, "Enter the plate number")


# =========================================
# VEHICLE PLATE
# =========================================
def handle_vehicle_plate_step(session, message):

    session.context["data"]["vehicle_plate_no"] = message.strip()

    session.context["step"] = ASK_VEHICLE_SEAT_CAP

    session.save()

    return send_text(session.phone_number, "How many seats does it have?")


# =========================================
# VEHICLE SEAT CAP
# =========================================
def handle_vehicle_seat_cap_step(session, message):

    try:

        seat_cap = int(message)

    except ValueError:

        return send_text(session.phone_number, "Seat capacity must be a number")

    data = session.context.get("data", {})

    vehicle, created = Vehicle.objects.get_or_create(user=session.user)

    vehicle.type = data.get("vehicle_type")

    vehicle.brand = data.get("vehicle_brand")

    vehicle.plate_no = data.get("vehicle_plate_no")

    vehicle.seat_cap = seat_cap

    vehicle.save()

    action = data.get("vehicle_action")

    reset_session(session)

    action_text = "updated" if action == "update" else "created"

    return send_text(
        session.phone_number, (f"Vehicle profile " f"{action_text} " f"successfully ✅")
    )

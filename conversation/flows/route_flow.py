from conversation.state.route_steps import *

from conversation.services.message_service import send_text

from conversation.ai.extractors.route_extractor import extract_route_data

from rideshare.services import (
    create_driver_route,
    get_driver_routes,
    update_driver_route,
    delete_driver_route,
)


def create_route(session, start_name, destination_name):

    route = create_driver_route(
        driver=session.user, start_name=start_name, end_name=destination_name
    )

    session.context = {"active_flow": None, "step": None, "data": {}}

    session.save()

    return send_text(
        session.phone_number,
        (
            "Route created successfully ✅\n\n"
            f"{route.start_name} → "
            f"{route.end_name}\n\n"
            "You can also:\n"
            "- create another route\n"
            "- view routes\n"
            "- update route"
        ),
    )


def start_route_flow(session, message):

    extracted = extract_route_data(message)

    start_name = extracted.get("start_name")

    destination_name = extracted.get("destination_name")

    # =====================================
    # ASK START LOCATION
    # =====================================

    if not start_name:

        session.context = {
            "active_flow": ROUTE_FLOW,
            "step": ASK_ROUTE_START,
            "data": {},
        }

        session.save()

        return send_text(
            session.phone_number, ("📍 Where does your " "route start from?")
        )

    # =====================================
    # ASK DESTINATION
    # =====================================

    if not destination_name:

        session.context = {
            "active_flow": ROUTE_FLOW,
            "step": ASK_ROUTE_DESTINATION,
            "data": {"route_start": start_name},
        }

        session.save()

        return send_text(session.phone_number, ("📍 Where is the " "destination?"))

    # =====================================
    # CREATE ROUTE IMMEDIATELY
    # =====================================

    return create_route(session, start_name, destination_name)


def handle_route_start(session, message):

    destination_name = session.context["data"].get("destination_name")

    if destination_name:

        return create_route(session, message, destination_name)

    session.context["data"]["route_start"] = message

    session.context["step"] = ASK_ROUTE_DESTINATION

    session.save()

    return send_text(session.phone_number, "📍 Where is the destination?")


def handle_route_destination(session, message):

    route_start = session.context["data"].get("route_start")

    return create_route(session, route_start, message)


def view_routes(session):

    routes = get_driver_routes(session.user)

    if not routes:

        return send_text(session.phone_number, "You don't have any routes yet.")

    message = "🚗 Your Routes:\n\n"

    # for r in routes:

    #     message += (
    #         f"{r.id}. {r.start_name} → {r.end_name}\n"
    #     )
    for index, route in enumerate(routes, start=1):

        message += f"{index}. " f"{route.start_name} → " f"{route.end_name}\n"

    message += "\nYou can say:\n" "- update route \n" "- create route"

    return send_text(session.phone_number, message)


def update_route(session, route_id, new_start=None, new_end=None):

    route = update_driver_route(
        driver=session.user, route_id=route_id, start_name=new_start, end_name=new_end
    )

    # =====================================
    # ROUTE NOT FOUND
    # =====================================

    if not route:

        return send_text(
            session.phone_number,
            ("Route not found.\n\n" "Say 'view routes' " "to see your routes."),
        )

    return send_text(
        session.phone_number,
        (
            "Route updated successfully ✅\n\n"
            f"{route.start_name} → "
            f"{route.end_name}"
        ),
    )


def start_update_route_flow(session):

    routes = get_driver_routes(session.user)

    if not routes:

        return send_text(session.phone_number, "You don't have any routes yet.")

    message = "Which route would " "you like to update?\n\n"

    for i, route in enumerate(routes, start=1):

        message += f"{i}. " f"{route.start_name} → " f"{route.end_name}\n"

    session.context = {
        "active_flow": ROUTE_FLOW,
        "step": ASK_ROUTE_TO_UPDATE,
        "data": {"route_ids": [route.id for route in routes]},
    }

    session.save()

    return send_text(session.phone_number, message)


# =========================================
# HANDLE ROUTE SELECTION
# =========================================
def handle_route_selection(session, message):

    try:

        selected_index = int(message) - 1

    except:

        return send_text(session.phone_number, "Please enter a valid number.")

    route_ids = session.context["data"].get("route_ids", [])

    if selected_index < 0 or selected_index >= len(route_ids):

        return send_text(session.phone_number, "Invalid route selection.")

    selected_route_id = route_ids[selected_index]

    session.context["data"]["selected_route_id"] = selected_route_id

    session.context["step"] = ASK_NEW_ROUTE_START

    session.save()

    return send_text(session.phone_number, ("Enter new starting " "location"))


# =========================================
# HANDLE NEW ROUTE START
# =========================================
def handle_new_route_start(session, message):

    session.context["data"]["new_route_start"] = message

    session.context["step"] = ASK_NEW_ROUTE_DESTINATION

    session.save()

    return send_text(session.phone_number, ("Enter new destination " "location"))


# =========================================
# HANDLE NEW ROUTE DESTINATION
# =========================================
def handle_new_route_destination(session, message):

    route_id = session.context["data"].get("selected_route_id")

    new_start = session.context["data"].get("new_route_start")

    route = update_driver_route(
        driver=session.user, route_id=route_id, start_name=new_start, end_name=message
    )

    # =====================================
    # ROUTE NOT FOUND
    # =====================================

    if not route:

        session.context = {"active_flow": None, "step": None, "data": {}}

        session.save()

        return send_text(
            session.phone_number, ("Route not found.\n\n" "Please try again.")
        )

    # =====================================
    # RESET FLOW
    # =====================================

    session.context = {"active_flow": None, "step": None, "data": {}}

    session.save()

    return send_text(
        session.phone_number,
        (
            "Route updated successfully ✅\n\n"
            f"{route.start_name} → "
            f"{route.end_name}"
        ),
    )


# =========================================
# START DELETE ROUTE FLOW
# =========================================
def start_delete_route_flow(session):

    routes = get_driver_routes(session.user)

    if not routes:

        return send_text(session.phone_number, ("You don't have any " "routes yet."))

    message = "Which route would " "you like to delete?\n\n"

    for i, route in enumerate(routes, start=1):

        message += f"{i}. " f"{route.start_name} → " f"{route.end_name}\n"

    session.context = {
        "active_flow": ROUTE_FLOW,
        "step": ASK_ROUTE_TO_DELETE,
        "data": {"route_ids": [route.id for route in routes]},
    }

    session.save()

    return send_text(session.phone_number, message)


# =========================================
# HANDLE ROUTE DELETE SELECTION
# =========================================
def handle_route_delete_selection(session, message):

    try:

        selected_index = int(message) - 1

    except:

        return send_text(session.phone_number, "Please enter a valid number.")

    route_ids = session.context["data"].get("route_ids", [])

    if selected_index < 0 or selected_index >= len(route_ids):

        return send_text(session.phone_number, "Invalid route selection.")

    selected_route_id = route_ids[selected_index]

    routes = get_driver_routes(session.user)

    selected_route = next(
        (route for route in routes if route.id == selected_route_id), None
    )

    if not selected_route:

        return send_text(session.phone_number, "Route not found.")

    session.context["data"]["selected_route_id"] = selected_route_id

    session.context["step"] = CONFIRM_ROUTE_DELETE

    session.save()

    return send_text(
        session.phone_number,
        (
            "Are you sure you want "
            "to delete this route?\n\n"
            f"{selected_route.start_name} → "
            f"{selected_route.end_name}\n\n"
            "Reply YES to confirm "
            "or NO to cancel."
        ),
    )


# =========================================
# HANDLE DELETE CONFIRMATION
# =========================================
def handle_route_delete_confirmation(session, message):

    response = message.strip().lower()

    # =====================================
    # CANCEL DELETE
    # =====================================

    if response in ["no", "cancel"]:

        session.context = {"active_flow": None, "step": None, "data": {}}

        session.save()

        return send_text(session.phone_number, "Route deletion cancelled.")

    # =====================================
    # INVALID RESPONSE
    # =====================================

    if response != "yes":

        return send_text(
            session.phone_number,
            ("Please reply with:\n\n" "YES → confirm deletion\n" "NO → cancel"),
        )

    # =====================================
    # DELETE ROUTE
    # =====================================

    route_id = session.context["data"].get("selected_route_id")

    route = delete_driver_route(driver=session.user, route_id=route_id)

    session.context = {"active_flow": None, "step": None, "data": {}}

    session.save()

    if not route:

        return send_text(
            session.phone_number, ("Route not found " "or already deleted.")
        )

    return send_text(
        session.phone_number,
        (
            "Route deleted successfully ❌\n\n"
            f"{route.start_name} → "
            f"{route.end_name}"
        ),
    )

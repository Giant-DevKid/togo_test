from conversation.flows.onboarding_flow import (
    start_onboarding_flow,
    handle_onboarding_flow,
)
from conversation.ai.generators.welcome_generator import generate_welcome_message
from conversation.flows.vehicle_flow import handle_vehicle_flow
from conversation.flows.booking_flow import handle_booking_flow
from conversation.flows.route_flow import *
from conversation.flows.rider_request_flow import *
from conversation.services.response_service import build_fallback_response
from conversation.services.message_service import send_text
from conversation.services.session_service import reset_session
from conversation.services.permission_service import can_access_intent
from conversation.services.access_message_service import get_access_denied_message
from conversation.ai.intent.detector import detect_intent
from conversation.state.onboarding_steps import ONBOARDING_FLOW
from conversation.state.vehicle_steps import VEHICLE_FLOW
from conversation.state.bank_steps import BANK_FLOW, BANK_UPDATE_FLOW
from conversation.state.route_steps import *
from conversation.state.booking_steps import BOOKING_FLOW
from conversation.state.payment_steps import PAYMENT_FLOW, AWAITING_PAYMENT
from conversation.flows.ride_completion_flow import handle_ride_completion_flow
from conversation.flows.bank_flow import (
    start_bank_flow,
    handle_bank_flow,
    view_bank_account,
    start_update_bank_flow,
)

from conversation.flows.payment_flow import handle_payment_flow
from conversation.ai.intent.intents import *

GLOBAL_EXIT_COMMANDS = ["cancel", "stop", "exit", "reset"]
GREETING_MESSAGES = [
    "hi",
    "hello",
    "hey",
    "yo",
    "start",
    "good morning",
    "good afternoon",
    "good evening",
]


def route_message(session, message):
    # =====================================
    # BUTTON PAYLOAD NORMALIZATION
    # =====================================

    BUTTON_MESSAGE_MAP = {

        # VEHICLE
        "create_vehicle": "add my vehicle",

        "update_vehicle": "update my vehicle",

        "vehicle_type_car": "car",

        "vehicle_type_bus": "bus",

        "vehicle_type_motorcycle": "motorcycle",

        # BANK
        "add_bank_account": "add bank account",

        "update_bank_account": "update bank account",

        "view_bank_account": "view bank account",

        # PAYMENT
        "pay_now": "pay now",

        "cancel_ride": "cancel ride",

        # ROUTES
        "create_route": "create route",

        "view_routes": "view my routes",

        # RIDES
        "view_ride_requests": "view ride requests",

        "view_ride_offers": "view ride offers",
    }

    # =====================================
    # CONVERT BUTTON ID TO TEXT
    # =====================================

    if message in BUTTON_MESSAGE_MAP:

        message = BUTTON_MESSAGE_MAP[message]

    # normalized_message = (
    #     message.strip().lower()
    # )

    normalized_message = message.strip().lower()

    # =====================================
    # EXIT COMMANDS
    # =====================================

    if normalized_message in GLOBAL_EXIT_COMMANDS:

        reset_session(session)

        return send_text(session.phone_number, "Current action cancelled.")

    # =====================================
    # ACTIVE FLOW CONTINUATION FIRST
    # =====================================

    active_flow = session.context.get("active_flow")

    # =====================================
    # CONTINUE ONBOARDING FLOW
    # =====================================

    if active_flow == ONBOARDING_FLOW:

        return handle_onboarding_flow(session, message)

    # =====================================
    # START ONBOARDING
    # =====================================

    if not session.user:

        return start_onboarding_flow(session)

    # =====================================
    # RETURNING USER GREETING
    # =====================================

    if normalized_message in GREETING_MESSAGES:

        session.context = {
            "active_flow": None,
            "step": None,
            "data": {},
        }

        session.save()

        welcome_message = generate_welcome_message(
            session.user,
            is_returning=True,
        )

        return send_text(
            session.phone_number,
            welcome_message,
        )

    # =====================================
    # VEHICLE FLOW
    # =====================================

    if active_flow == VEHICLE_FLOW:

        return handle_vehicle_flow(session, message, None)

    # =====================================
    # BANK FLOW
    # =====================================

    if active_flow in [BANK_FLOW, BANK_UPDATE_FLOW]:

        return handle_bank_flow(session, message)

    # =====================================
    # BOOKING FLOW
    # =====================================

    if active_flow == BOOKING_FLOW:

        return handle_booking_flow(session, message, None)

    # =====================================
    # RIDE OFFER FLOW
    # =====================================

    if active_flow == RIDE_OFFER_FLOW:

        step = session.context.get("step")

        if step == SELECTING_RIDER:

            return handle_rider_selection(session, message)

    # =====================================
    # RIDE OFFER PYMENT FLOW
    # =====================================
    print("ACTIVE FLOW:", active_flow)

    print("SESSION CONTEXT:", session.context)
    if active_flow == PAYMENT_FLOW:

        step = session.context.get("step")

        if step == AWAITING_PAYMENT:

            return handle_payment_flow(session, message)

    # =====================================
    # ROUTE FLOW
    # =====================================

    if active_flow == ROUTE_FLOW:

        step = session.context.get("step")

        if step == ASK_ROUTE_START:

            return handle_route_start(session, message)

        if step == ASK_ROUTE_DESTINATION:

            return handle_route_destination(session, message)

        if step == ASK_ROUTE_TO_UPDATE:

            return handle_route_selection(session, message)

        if step == ASK_NEW_ROUTE_START:

            return handle_new_route_start(session, message)

        if step == ASK_NEW_ROUTE_DESTINATION:

            return handle_new_route_destination(session, message)

        if step == ASK_ROUTE_TO_DELETE:

            return handle_route_delete_selection(session, message)

        if step == CONFIRM_ROUTE_DELETE:

            return handle_route_delete_confirmation(session, message)

    # =====================================
    # DRIVER REQUEST ACTIONS
    # =====================================

    driver_action_response = handle_driver_request_action(session, message)

    if driver_action_response:

        return driver_action_response

    # =====================================
    # DETECT INTENT
    # =====================================

    intent = detect_intent(message)

    print("AI INTENT:", intent)

    # =====================================
    # PERMISSION CHECK
    # =====================================

    if not can_access_intent(session.user, intent):

        return send_text(
            session.phone_number, get_access_denied_message(session.user, intent)
        )

    # =====================================
    # GLOBAL FEATURES
    # =====================================

    if intent == VIEW_RIDES:

        return view_ride_offers(session)

    # =====================================
    # ROUTE FEATURES
    # =====================================

    if intent == CREATE_ROUTE:

        return start_route_flow(session, message)

    if intent == VIEW_ROUTES:

        return view_routes(session)

    if intent == UPDATE_ROUTE:

        return start_update_route_flow(session)

    if intent == DELETE_ROUTE:

        return start_delete_route_flow(session)

    # =====================================
    # VEHICLE FEATURES
    # =====================================

    if intent in [VIEW_VEHICLE, CREATE_VEHICLE, UPDATE_VEHICLE]:

        return handle_vehicle_flow(session, message, intent)

    # =====================================
    # BANK FLOW START
    # =====================================
    if intent == VIEW_BANK_ACCOUNT:

        return view_bank_account(session)

    if intent == UPDATE_BANK_ACCOUNT:

        return start_update_bank_flow(session)

    if intent == ADD_BANK_ACCOUNT:

        return start_bank_flow(session)

    # =====================================
    # BOOKING FEATURES
    # =====================================

    if intent in [BOOK_RIDE, UPDATE_BOOKING, CANCEL_BOOKING]:

        return handle_booking_flow(session, message, intent)

    # =====================================
    # RIDER REQUESTS
    # =====================================

    if intent == VIEW_RIDE_REQUESTS:

        return view_ride_requests(session)

    # =====================================
    # VIEW RIDE OFFERS
    # =====================================

    if intent == VIEW_RIDE_OFFERS:

        return view_ride_offers(session)

    # =====================================
    # VIEW RIDE OFFERS
    # =====================================

    if intent in [REQUEST_RIDE_OTP, VERIFY_RIDE_OTP]:

        return handle_ride_completion_flow(session, message)

    # =====================================
    # FALLBACK
    # =====================================

    return send_text(session.phone_number, build_fallback_response(session.user))

from conversation.constants import (
    ASK_SERVICE_PROVIDER_ROLE,
    ASK_FIRST_NAME,
)

from whatsapp.services import (
    send_whatsapp_buttons,
    send_whatsapp_message,
)

from conversation.services.menu_service import (
    get_user_menu
)
from conversation.constants import MAIN_MENU

from django.core.exceptions import ValidationError

from conversation.constants import *
from account.services import (
    create_user_account,
    send_verification_otp,
    verify_user_otp,
)


def handle_start(session, message):

    if session.user and session.user.is_verified:

        return show_main_menu(session)

    session.state = ASK_MAIN_ROLE
    session.save()
    response = send_whatsapp_buttons(
        to=session.phone_number,
        body_text="Welcome 🚗\n\nChoose your role",
        buttons=[

            {
                "id": "passenger",
                "title": "Passenger"
            },

            {
                "id": "rider",
                "title": "Rider"
            },

            {
                "id": "service_provider",
                "title": "Service"
            }
        ]
    )

    print("WHATSAPP RESPONSE:", response)

def handle_main_role(session, message):

    if message == "service_provider":

        session.state = (
            ASK_SERVICE_PROVIDER_ROLE
        )

        session.save()

        return send_whatsapp_buttons(

            to=session.phone_number,

            body_text=(
                "Choose service type"
            ),

            buttons=[

                {
                    "id": "event_organiser",
                    "title": "Event"
                },

                {
                    "id": "tour_guide",
                    "title": "Tour Guide"
                }
            ]
        )

    allowed_roles = [
        "passenger",
        "rider",
    ]

    if message not in allowed_roles:

        return send_whatsapp_message(
            session.phone_number,
            "Invalid role"
        )

    session.context["user_type"] = message

    session.state = ASK_FIRST_NAME

    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "Enter first name"
    )

def handle_service_provider_role(session, message):

    allowed_roles = [
        "event_organiser",
        "tour_guide"
    ]

    if message not in allowed_roles:

        return send_whatsapp_message(
            session.phone_number,
            "Invalid service type"
        )

    session.context["user_type"] = message

    session.state = ASK_FIRST_NAME

    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "Enter first name"
    )

def handle_first_name(session, message):

    first_name = message.strip()

    session.context["first_name"] = first_name

    session.state = ASK_LAST_NAME
    session.save()

    response = send_whatsapp_message(
        session.phone_number,
        "Enter your last name"
    )

    print("WHATSAPP RESPONSE:", response)

def handle_last_name(session, message):

    last_name = message.strip()

    session.context["last_name"] = last_name

    session.state = ASK_EMAIL
    session.save()

    response = send_whatsapp_message(
        session.phone_number,
        "Enter your email address"
    )

    print("WHATSAPP RESPONSE:", response)

def handle_email(session, message):

    email = message.strip().lower()

    try:

        user = create_user_account(
            email=email,
            user_type=session.context["user_type"],
            phone_no=session.phone_number
        )

    except ValidationError as e:

        response = send_whatsapp_message(
            session.phone_number,
            str(e)
        )

        print("WHATSAPP RESPONSE:", response)

        return

    user.first_name = session.context.get("first_name")
    user.last_name = session.context.get("last_name")

    user.save()

    try:

        send_verification_otp(user)

    except Exception as e:

        print("OTP ERROR:", str(e))

        send_whatsapp_message(
            session.phone_number,
            (
                "Unable to send OTP email right now.\n"
                "Please try again later."
            )
        )

        return

    session.user = user
    session.state = VERIFY_OTP

    session.save()

    response = send_whatsapp_message(
        session.phone_number,
        "OTP has been sent to your email.\n\nEnter OTP"
    )

    print("WHATSAPP RESPONSE:", response)

def handle_otp(session, message):

    success, response_message = verify_user_otp(
        session.user,
        message
    )

    if not success:

        response = send_whatsapp_message(
            session.phone_number,
            response_message
        )

        print("WHATSAPP RESPONSE:", response)
        return

    session.state = MAIN_MENU

    session.save()

    # Send success message first
    response = send_whatsapp_message(
        session.phone_number,
        (
            f"Welcome "
            f"{session.user.first_name} 🎉\n\n"
            f"Your account has been verified successfully."
        )
    )

    print("WHATSAPP RESPONSE:", response)

    #show role-based menu
    return show_main_menu(session)

def handle_main_menu(session, message):

    user = session.user

    # =========================
    # PASSENGER ACTIONS
    # =========================

    if message == "book_ride":

        send_whatsapp_message(
            session.phone_number,
            "Ride booking flow coming in Phase 2 🚗"
        )

        return show_main_menu(session)

    # =========================
    # EVENT ORGANISER ACTIONS
    # =========================

    if message == "create_event":

        session.state = "ASK_EVENT_NAME"

        session.save()

        return send_whatsapp_message(
            session.phone_number,
            "🏷 Enter event name"
        )

    
    elif message == "my_events":

        send_whatsapp_message(
            session.phone_number,
            "Your events dashboard coming soon 📅"
        )

        return show_main_menu(session)

    # =========================
    # TOUR GUIDE ACTIONS
    # =========================

    elif message == "create_tour":

        send_whatsapp_message(
            session.phone_number,
            "Tour creation flow coming soon 🌍"
        )

        return show_main_menu(session)

    elif message == "my_tours":

        send_whatsapp_message(
            session.phone_number,
            "Your tours dashboard coming soon 🧳"
        )

        return show_main_menu(session)

    # =========================
    # SHARED ACTIONS
    # =========================

    elif message == "profile":

        profile_text = (
            f"👤 Profile\n\n"
            f"Name: {user.first_name} {user.last_name}\n"
            f"Email: {user.email}\n"
            f"Role: {user.user_type}"
        )

        send_whatsapp_message(
            session.phone_number,
            profile_text
        )

        return show_main_menu(session)

    elif message == "support":

        send_whatsapp_message(
            session.phone_number,
            "Support will contact you shortly."
        )

        return show_main_menu(session)

    else:

        return show_main_menu(session)

def show_main_menu(session):

    user = session.user

    menu_buttons = get_user_menu(
        user.user_type
    )

    session.state = MAIN_MENU

    session.save()

    return send_whatsapp_buttons(
        to=session.phone_number,
        body_text=(
            f"Welcome back "
            f"{user.first_name} 👋"
        ),
        buttons=menu_buttons
    )



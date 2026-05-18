
from whatsapp.services import (
    send_whatsapp_message,
)

from conversation.handlers.onboarding import (
    show_main_menu,
)


def create_tour_handler(session):

    session.state = "CREATE_TOUR"

    session.save()

    send_whatsapp_message(
        session.phone_number,
        "🧳 Tour creation started"
    )

    return show_main_menu(session)


def my_tours_handler(session):

    send_whatsapp_message(
        session.phone_number,
        "🗺️ Your tours will appear here"
    )

    return show_main_menu(session)

from event.services import create_event

from whatsapp.services import send_whatsapp_message

from conversation.handlers.onboarding import (
    show_main_menu
)



def handle_event_name(session, message):

    session.context["event_name"] = message.strip()

    session.state = "ASK_EVENT_LOCATION"
    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "📍 Enter event location"
    )


def handle_event_location(session, message):

    session.context["location"] = message.strip()

    session.state = "ASK_EVENT_START_DATE"
    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "📅 Enter start date (YYYY-MM-DD)"
    )


def handle_event_start_date(session, message):

    session.context["start_date"] = message.strip()

    session.state = "ASK_EVENT_END_DATE"
    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "📅 Enter end date (YYYY-MM-DD)"
    )


def handle_event_end_date(session, message):

    session.context["end_date"] = message.strip()

    session.state = "ASK_EVENT_START_TIME"
    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "⏰ Enter start time (HH:MM)"
    )


def handle_event_start_time(session, message):

    session.context["start_time"] = message.strip()

    session.state = "ASK_EVENT_END_TIME"
    session.save()

    return send_whatsapp_message(
        session.phone_number,
        "⏰ Enter end time (HH:MM)"
    )


def handle_event_end_time(session, message):

    session.context["end_time"] = message.strip()

    # CREATE EVENT
    event = create_event(
        organizer=session.user,
        data=session.context
    )

    session.context["event_id"] = event.id

    session.state = "MAIN_MENU"
    session.context["flow"] = None
    session.save()

    send_whatsapp_message(
        session.phone_number,
        f"🎉 Event Created Successfully!\n\n"
        f"Name: {event.event_name}\n"
        f"Location: {event.location}"
    )
    return show_main_menu(session)


from whatsapp.services import (
    send_interactive_buttons_message
)

from conversation.submenu_config.passenger_menu import (
    PASSENGER_MENU
)

from conversation.submenu_config.rider_menu import (
    RIDER_MENU
)

from conversation.submenu_config.event_menu import (
    EVENT_MENU
)

from conversation.submenu_config.tour_menu import (
    TOUR_MENU
)


MENU_MAP = {
    "passenger": PASSENGER_MENU,
    "rider": RIDER_MENU,
    "event_organiser": EVENT_MENU,
    "tour_guide": TOUR_MENU,
}


def get_user_menu(user_type):

    return MENU_MAP.get(user_type, [])


def send_passenger_menu(phone_number):

    return send_interactive_buttons_message(

        to=phone_number,

        body="Passenger Menu",

        buttons=[

            {
                "id": "PASSENGER_PROFILE",
                "title": "Profile"
            },

            {
                "id": "PASSENGER_BOOKINGS",
                "title": "Bookings"
            },

            {
                "id": "PASSENGER_SUPPORT",
                "title": "Support"
            },
        ]
    )


def send_rider_menu(phone_number):

    return send_interactive_buttons_message(

        to=phone_number,

        body="Rider Menu",

        buttons=[

            {
                "id": "RIDER_PROFILE",
                "title": "Profile"
            },

            {
                "id": "RIDER_ORDERS",
                "title": "Orders"
            },

            {
                "id": "RIDER_SUPPORT",
                "title": "Support"
            },
        ]
    )


def send_tour_guide_menu(phone_number):

    return send_interactive_buttons_message(

        to=phone_number,

        body="Tour Guide Menu",

        buttons=[

            {
                "id": "TOUR_GUIDE_PROFILE",
                "title": "Profile"
            },

            {
                "id": "TOUR_GUIDE_TOURS",
                "title": "My Tours"
            },

            {
                "id": "TOUR_GUIDE_SUPPORT",
                "title": "Support"
            },
        ]
    )


def send_event_organiser_menu(phone_number):

    return send_interactive_buttons_message(

        to=phone_number,

        body="Event Organiser Menu",

        buttons=[

            {
                "id": "EVENT_PROFILE",
                "title": "Profile"
            },

            {
                "id": "EVENT_MY_EVENTS",
                "title": "My Events"
            },

            {
                "id": "EVENT_SUPPORT",
                "title": "Support"
            },
        ]
    )


def send_role_based_menu(user):

    role = (
        user.user_type.lower()
    )

    if role == "passenger":

        return send_passenger_menu(
            user.phone_no
        )

    elif role == "rider":

        return send_rider_menu(
            user.phone_no
        )

    elif role == "tour guide":

        return send_tour_guide_menu(
            user.phone_no
        )

    elif role == "event organiser":

        return send_event_organiser_menu(
            user.phone_no
        )
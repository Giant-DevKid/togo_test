
from conversation.action_registry.global_actions import (
    get_action_handler
)

from conversation.handlers.onboarding import (
    show_main_menu
)

from whatsapp.services import (
    send_whatsapp_message
)


# def handle_main_menu(
#     session,
#     message
# ):
#     print("MAIN MENU MESSAGE:", message)

#     handler = get_action_handler(
#         session.user.user_type,
#         message
#     )

#     print("HANDLER:", handler)

#     if not handler:

#         return show_main_menu(session)

#     return handler(session)
def handle_main_menu(
    session,
    message
):

    print(
        "MAIN MENU MESSAGE:",
        message
    )

    handler, extra_data = (
        get_action_handler(
            session.user.user_type,
            message
        )
    )

    print("HANDLER:", handler)

    print(
        "EXTRA DATA:",
        extra_data
    )

    if not handler:

        return show_main_menu(
            session
        )

    # =====================================
    # DYNAMIC ACTIONS
    # =====================================
    if extra_data is not None:

        return handler(
            session,
            extra_data
        )

    # =====================================
    # NORMAL ACTIONS
    # =====================================
    return handler(session)


def handle_rider_profile_menu(
    session,
    message
):

    handler, extra_data = (
        get_action_handler(
            session.user.user_type,
            message
        )
    )

    print("HANDLER:", handler)

    print(
        "EXTRA DATA:",
        extra_data
    )

    if not handler:

        return send_whatsapp_message(

            session.phone_number,

            "Invalid profile option"
        )

    # =====================================
    # DYNAMIC ACTIONS
    # =====================================
    if extra_data is not None:

        return handler(
            session,
            extra_data
        )

    # =====================================
    # NORMAL ACTIONS
    # =====================================
    return handler(session)


def handle_rider_route_menu(
    session,
    message
):

    handler, extra_data = (
        get_action_handler(
            session.user.user_type,
            message
        )
    )

    print("HANDLER:", handler)

    print(
        "EXTRA DATA:",
        extra_data
    )

    if not handler:

        return send_whatsapp_message(

            session.phone_number,

            "Invalid route option"
        )

    # =====================================
    # DYNAMIC ACTIONS
    # =====================================
    if extra_data is not None:

        return handler(
            session,
            extra_data
        )

    # =====================================
    # NORMAL ACTIONS
    # =====================================
    return handler(session)

# def handle_rider_profile_menu(
#     session,
#     message
# ):

#     handler = get_action_handler(
#         session.user.user_type,
#         message
#     )

#     if not handler:

#         return send_whatsapp_message(
#             session.phone_number,
#             "Invalid profile option"
#         )

#     return handler(session)

# def handle_rider_route_menu(
#     session,
#     message
# ):

#     handler = get_action_handler(
#         session.user.user_type,
#         message
#     )

#     if not handler:

#         return

#     return handler(session)



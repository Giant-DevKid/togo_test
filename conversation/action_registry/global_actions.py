
# from conversation.action_registry.passenger_actions import (
#     PASSENGER_ACTIONS
# )

# from conversation.action_registry.rider_actions import (
#     RIDER_ACTIONS
# )

# from conversation.action_registry.event_actions import (
#     EVENT_ACTIONS
# )

# from conversation.action_registry.tour_actions import (
#     TOUR_ACTIONS
# )

# from conversation.handlers.common import (
#     go_back_main_menu_handler
# )


# ACTION_MAP = {
#     "passenger": PASSENGER_ACTIONS,
#     "rider": RIDER_ACTIONS,
#     "event_organiser": EVENT_ACTIONS,
#     "tour_guide": TOUR_ACTIONS,
# }

# GLOBAL_ACTIONS = {

#     "go_back_main_menu":
#         go_back_main_menu_handler,
# }


# def get_action_handler(
#     user_type,
#     action
# ):

#     if action in GLOBAL_ACTIONS:

#         return GLOBAL_ACTIONS[action]
    
#     role_actions = ACTION_MAP.get(
#         user_type,
#         {}
#     )
    

#     return role_actions.get(action)


from conversation.action_registry.passenger_actions import (
    PASSENGER_ACTIONS
)

from conversation.action_registry.rider_actions import (
    RIDER_ACTIONS
)

from conversation.action_registry.event_actions import (
    EVENT_ACTIONS
)

from conversation.action_registry.tour_actions import (
    TOUR_ACTIONS
)

from conversation.handlers.common import (
    go_back_main_menu_handler
)

from conversation.handlers.rider import (

    rider_accept_booking_handler,

    rider_reject_booking_handler,

    rider_change_price_handler,
)

from conversation.handlers.passenger import (

    passenger_select_rider_handler,

    proceed_payment_handler,

    cancel_booking_handler,
)


ACTION_MAP = {

    "passenger":
        PASSENGER_ACTIONS,

    "rider":
        RIDER_ACTIONS,

    "event_organiser":
        EVENT_ACTIONS,

    "tour_guide":
        TOUR_ACTIONS,
}


GLOBAL_ACTIONS = {

    "go_back_main_menu":
        go_back_main_menu_handler,
}


# =========================================
# DYNAMIC ACTION ROUTER
# =========================================

def get_dynamic_action_handler(
    action
):

    # =====================================
    # ACCEPT BOOKING
    # =====================================
    if action.startswith(
        "accept_booking_"
    ):

        booking_id = (
            action.split("_")[-1]
        )

        return (

            rider_accept_booking_handler,

            booking_id
        )

    # =====================================
    # REJECT BOOKING
    # =====================================
    if action.startswith(
        "reject_booking_"
    ):

        booking_id = (
            action.split("_")[-1]
        )

        return (

            rider_reject_booking_handler,

            booking_id
        )

    # =====================================
    # CHANGE PRICE
    # =====================================
    if action.startswith(
        "change_price_"
    ):

        booking_id = (
            action.split("_")[-1]
        )

        return (

            rider_change_price_handler,

            booking_id
        )

    # =====================================
    # SELECT RIDER
    # =====================================
    if action.startswith(
        "select_rider_"
    ):

        response_id = (
            action.split("_")[-1]
        )

        return (

            passenger_select_rider_handler,

            response_id
        )

    # =====================================
    # PROCEED PAYMENT
    # =====================================
    if action.startswith(
        "proceed_payment_"
    ):

        booking_id = (
            action.split("_")[-1]
        )

        return (

            proceed_payment_handler,

            booking_id
        )

    # =====================================
    # CANCEL BOOKING
    # =====================================
    if action.startswith(
        "cancel_booking_"
    ):

        booking_id = (
            action.split("_")[-1]
        )

        return (

            cancel_booking_handler,

            booking_id
        )

    return None


# =========================================
# MAIN ACTION RESOLVER
# =========================================

def get_action_handler(
    user_type,
    action
):

    # =====================================
    # GLOBAL ACTIONS
    # =====================================
    if action in GLOBAL_ACTIONS:

        return (
            GLOBAL_ACTIONS[action],
            None
        )

    # =====================================
    # DYNAMIC ACTIONS
    # =====================================
    dynamic_handler = (
        get_dynamic_action_handler(
            action
        )
    )

    if dynamic_handler:

        return dynamic_handler

    # =====================================
    # STATIC ROLE ACTIONS
    # =====================================
    role_actions = ACTION_MAP.get(
        user_type,
        {}
    )

    handler = role_actions.get(
        action
    )

    if handler:

        return (
            handler,
            None
        )

    return (None, None)
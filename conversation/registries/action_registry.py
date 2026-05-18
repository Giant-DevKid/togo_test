# # from conversation.action_registry.rider_actions import (
# #     RIDER_ACTIONS
# # )

# # from conversation.action_registry.global_actions import (
# #     GLOBAL_ACTIONS
# # )

# # ACTION_REGISTRY = {}

# # ACTION_REGISTRY.update(GLOBAL_ACTIONS)

# # ACTION_REGISTRY.update(RIDER_ACTIONS)


# from conversation.handlers.menu_handler import (

#     handle_profile_menu,

#     handle_passenger_bookings,

#     handle_rider_orders,

#     handle_tour_guide_tours,

#     handle_event_organiser_events,

#     handle_go_back,
# )


# ACTION_REGISTRY = {

#     # =====================================
#     # PASSENGER
#     # =====================================

#     "PASSENGER_PROFILE":
#         handle_profile_menu,

#     "PASSENGER_BOOKINGS":
#         handle_passenger_bookings,


#     # =====================================
#     # RIDER
#     # =====================================

#     "RIDER_PROFILE":
#         handle_profile_menu,

#     "RIDER_ORDERS":
#         handle_rider_orders,


#     # =====================================
#     # TOUR GUIDE
#     # =====================================

#     "TOUR_GUIDE_PROFILE":
#         handle_profile_menu,

#     "TOUR_GUIDE_TOURS":
#         handle_tour_guide_tours,


#     # =====================================
#     # EVENT ORGANISER
#     # =====================================

#     "EVENT_PROFILE":
#         handle_profile_menu,

#     "EVENT_MY_EVENTS":
#         handle_event_organiser_events,


#     # =====================================
#     # GLOBAL
#     # =====================================

#     "GO_BACK_MAIN_MENU":
#         handle_go_back,
# }


from conversation.action_registry.passenger_actions import (
    PASSENGER_ACTIONS
)

from conversation.action_registry.rider_actions import (
    RIDER_ACTIONS
)

from conversation.action_registry.booking_actions import (
    BOOKING_ACTIONS
)

ACTION_REGISTRY = {

    **PASSENGER_ACTIONS,

    **RIDER_ACTIONS,

    **BOOKING_ACTIONS,
}

from conversation.handlers.rider import (
    rider_profile_menu_handler,
    my_profile_handler,
    vehicle_profile_handler,
    ride_orders_handler,
    add_vehicle_handler,
    update_vehicle_handler,
    route_profile_handler,
    create_route_handler,
    my_routes_handler,
    rider_accept_booking_handler,
    rider_reject_booking_handler,
)

RIDER_ACTIONS = {

    # Main menu actions
    "rider_profile_menu": (
        rider_profile_menu_handler
    ),

    "ride_orders": (
        ride_orders_handler
    ),

    # Profile submenu actions
    "my_profile": (
        my_profile_handler
    ),

    "vehicle_profile": (
        vehicle_profile_handler
    ),

    "route_profile":
        route_profile_handler,

    "create_route":
        create_route_handler,

    "my_routes":
        my_routes_handler,

    "add_vehicle":
        add_vehicle_handler,

    "update_vehicle":
        update_vehicle_handler,

    "accept_booking":
        rider_accept_booking_handler,

    "reject_booking":
        rider_reject_booking_handler,
}
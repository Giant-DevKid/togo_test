from conversation.constants import *

from conversation.handlers.passenger import (

    handle_pickup_location,

    handle_destination_location,

    handle_select_rider,

    handle_confirm_booking,
)

PASSENGER_STATES = {

    ASK_PICKUP_LOCATION:
        handle_pickup_location,

    ASK_DESTINATION_LOCATION:
        handle_destination_location,

    SELECT_RIDER:
        handle_select_rider,

    CONFIRM_BOOKING:
        handle_confirm_booking,
}
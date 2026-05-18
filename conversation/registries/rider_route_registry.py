from conversation.constants import *

from conversation.handlers.rider import (

    handle_route_start,

    handle_route_destination,
)

RIDER_ROUTE_STATES = {

    ASK_ROUTE_START:
        handle_route_start,

    ASK_ROUTE_DESTINATION:
        handle_route_destination,
}
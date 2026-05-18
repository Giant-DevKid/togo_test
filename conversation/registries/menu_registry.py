
from conversation.constants import *

from conversation.handlers.menu_router import (
    handle_main_menu,
    handle_rider_profile_menu,
    handle_rider_route_menu,
)

MENU_STATES = {

    MAIN_MENU:
        handle_main_menu,

    RIDER_PROFILE_MENU:
        handle_rider_profile_menu,
    
    RIDER_ROUTE_MENU:
        handle_rider_route_menu,
}
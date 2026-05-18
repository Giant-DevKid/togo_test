
from conversation.registries.onboarding_registry import (
    ONBOARDING_STATES
)

from conversation.registries.menu_registry import (
    MENU_STATES
)

from conversation.registries.rider_registry import (
    RIDER_STATES
)

from conversation.registries.passenger_registry import (
    PASSENGER_STATES
)

from conversation.registries.event_registry import (
    EVENT_STATES
)

from conversation.action_registry.booking_actions import (
    BOOKING_ACTIONS
)

from conversation.registries.rider_route_registry import (
    RIDER_ROUTE_STATES
)

STATE_REGISTRY = {

    **ONBOARDING_STATES,

    **MENU_STATES,

    **RIDER_STATES,

    **RIDER_ROUTE_STATES,

    **PASSENGER_STATES,

    **EVENT_STATES,
    
    **BOOKING_ACTIONS,
}
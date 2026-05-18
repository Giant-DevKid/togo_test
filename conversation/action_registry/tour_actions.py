
from conversation.handlers.tour_guide import (
    create_tour_handler,
    my_tours_handler,
)

TOUR_ACTIONS = {
    "create_tour": create_tour_handler,
    "my_tours": my_tours_handler,
}
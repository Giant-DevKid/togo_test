
from conversation.handlers.passenger import (
    start_ride_booking,
    show_passenger_bookings,
)

PASSENGER_ACTIONS = {
    "book_ride": start_ride_booking,
    "my_bookings": show_passenger_bookings,
}
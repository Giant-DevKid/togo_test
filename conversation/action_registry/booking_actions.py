from conversation.handlers.passenger import (

    start_ride_booking,

    show_passenger_bookings,

    select_rider_handler,

    proceed_to_payment_handler,

    cancel_booking_handler,
)

BOOKING_ACTIONS = {

    "book_ride":
        start_ride_booking,

    "my_bookings":
        show_passenger_bookings,

    "select_rider":
        select_rider_handler,

    "proceed_payment":
        proceed_to_payment_handler,

    "cancel_booking":
        cancel_booking_handler,
}
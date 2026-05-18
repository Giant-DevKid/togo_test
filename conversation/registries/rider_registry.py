
from conversation.constants import *

from conversation.handlers.rider import (
    handle_vehicle_type,
    handle_vehicle_brand,
    handle_vehicle_plate_no,
    handle_vehicle_seat_cap,
    handle_new_booking_price,
)
 
RIDER_STATES = {

    ASK_VEHICLE_TYPE:
        handle_vehicle_type,

    ASK_VEHICLE_BRAND:
        handle_vehicle_brand,

    ASK_VEHICLE_PLATE_NO:
        handle_vehicle_plate_no,

    ASK_VEHICLE_SEAT_CAP:
        handle_vehicle_seat_cap,

    ASK_NEW_BOOKING_PRICE:
        handle_new_booking_price,
}

from conversation.handlers.event_organiser import (
    handle_event_name,
    handle_event_location,
    handle_event_start_date,
    handle_event_end_date,
    handle_event_start_time,
    handle_event_end_time,
)

EVENT_STATES = {

    "ASK_EVENT_NAME":
        handle_event_name,

    "ASK_EVENT_LOCATION":
        handle_event_location,

    "ASK_EVENT_START_DATE":
        handle_event_start_date,

    "ASK_EVENT_END_DATE":
        handle_event_end_date,

    "ASK_EVENT_START_TIME":
        handle_event_start_time,

    "ASK_EVENT_END_TIME":
        handle_event_end_time,
}

from .models import Event


def create_event(
    organizer,
    data
):

    return Event.objects.create(
        organizer=organizer,
        event_name=data["event_name"],
        location=data["location"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        start_time=data["start_time"],
        end_time=data["end_time"],
    )
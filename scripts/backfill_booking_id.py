from rideshare.models import RideBooking
from rideshare.utils.id_generator import generate_booking_id


def run():

    bookings = RideBooking.objects.filter(booking_id__isnull=True)

    for booking in bookings:

        new_id = generate_booking_id()

        while RideBooking.objects.filter(booking_id=new_id).exists():

            new_id = generate_booking_id()

        booking.booking_id = new_id
        booking.save()

    print("Backfill complete")

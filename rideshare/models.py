import uuid
from django.db import models


from account.models import User


def upload_data(instance, filename):

    return (
        f"vehicles/"
        f"{instance.user.id}/"
        f"{filename}"
    )


class Vehicle(models.Model):

    VEHICLE_TYPES = [
        ("Car", "Car"),
        ("Bus", "Bus"),
        ("Tricycle", "Tricycle"),
        ("Motorcycle", "Motorcycle"),
        ("Bicycle", "Bicycle"),
        ("Train", "Train"),
        ("Boat", "Boat"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vehicle"
    )

    licence = models.FileField(
        upload_to=upload_data,
        null=True,
        blank=True
    )

    type = models.CharField(
        null=True,
        choices=VEHICLE_TYPES,
        max_length=20
    )

    brand = models.CharField(
        null=True,
        max_length=125
    )

    plate_no = models.CharField(
        null=True,
        max_length=125,
        unique=True
    )

    seat_cap = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.user.email} - "
            f"{self.plate_no}"
        )


# -------------------------------------Ride Booking ------------------------------------------------

class DriverRoute(models.Model):

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="driver_routes"
    )

    start_name = models.CharField(
        max_length=255
    )

    end_name = models.CharField(
        max_length=255
    )

    start_lat = models.FloatField()

    start_lng = models.FloatField()

    end_lat = models.FloatField()

    end_lng = models.FloatField()

    distance_meters = models.FloatField()

    duration_seconds = models.FloatField()

    encoded_polyline = models.TextField()

    route_geometry = models.JSONField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class RideBooking(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        (
            "RIDER_SELECTED",
            "Rider Selected"
        ),

        (
            "PAYMENT_PENDING",
            "Payment Pending"
        ),

        ("CONFIRMED", "Confirmed"),

        (
            "OTP_VERIFICATION",
            "OTP Verification"
        ),

        ("COMPLETED", "Completed"),

        ("CANCELLED", "Cancelled"),
    ]

    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="passenger_bookings"
    )

    selected_rider = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_bookings"
    )

    pickup_name = models.CharField(
        max_length=255
    )

    destination_name = models.CharField(
        max_length=255
    )

    pickup_lat = models.FloatField()

    pickup_lng = models.FloatField()

    destination_lat = models.FloatField()

    destination_lng = models.FloatField()

    estimated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    distance_meters = models.FloatField()

    route_geometry = models.JSONField()

    encoded_polyline = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class RideBookingResponse(models.Model):

    RESPONSE_CHOICES = [

        ("PENDING", "Pending"),

        ("PAYMENT_PENDING", "Payment Pending"),

        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),

        ("CANCELLED", "Cancelled"),
    ]

    booking = models.ForeignKey(
        RideBooking,
        on_delete=models.CASCADE,
        related_name="responses"
    )

    rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    route = models.ForeignKey(
        DriverRoute,
        on_delete=models.CASCADE
    )

    response = models.CharField(
        max_length=50,
        choices=RESPONSE_CHOICES
    )

    updated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class RideOTP(models.Model):

    booking = models.OneToOneField(
        RideBooking,
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=6
    )

    is_verified = models.BooleanField(
        default=False
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
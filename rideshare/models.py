import uuid
from django.db import models
from decimal import Decimal, ROUND_HALF_UP


from account.models import User


def upload_data(instance, filename):

    return f"vehicles/" f"{instance.user.id}/" f"{filename}"


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
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="vehicle"
    )

    licence = models.FileField(upload_to=upload_data, null=True, blank=True)

    type = models.CharField(null=True, choices=VEHICLE_TYPES, max_length=20)

    brand = models.CharField(null=True, max_length=125)

    plate_no = models.CharField(null=True, max_length=125, unique=True)

    seat_cap = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return f"{self.user.email} - " f"{self.plate_no}"


# -------------------------------------Ride Booking ------------------------------------------------


class DriverRoute(models.Model):

    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="driver_routes"
    )

    start_name = models.CharField(max_length=255)

    end_name = models.CharField(max_length=255)

    start_lat = models.FloatField()

    start_lng = models.FloatField()

    end_lat = models.FloatField()

    end_lng = models.FloatField()

    distance_meters = models.FloatField()

    duration_seconds = models.FloatField()

    encoded_polyline = models.TextField()

    route_geometry = models.JSONField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)


class RideBooking(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RIDER_SELECTED", "Rider Selected"),
        ("PAYMENT_PENDING", "Payment Pending"),
        ("CONFIRMED", "Confirmed"),
        ("IN_PROGRESS", "In Progress"),
        ("OTP_PENDING", "OTP Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    passenger = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="passenger_bookings"
    )

    selected_rider = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_bookings",
    )
    booking_id = models.CharField(
        max_length=50, unique=True, editable=False, db_index=True
    )
    pickup_name = models.CharField(max_length=255)

    destination_name = models.CharField(max_length=255)

    pickup_lat = models.FloatField()

    pickup_lng = models.FloatField()

    destination_lat = models.FloatField()

    destination_lng = models.FloatField()

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2)

    final_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    distance_meters = models.FloatField()

    route_geometry = models.JSONField()

    encoded_polyline = models.TextField()

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")
    ride_completion_otp = models.CharField(max_length=10, null=True, blank=True)

    otp_generated_at = models.DateTimeField(null=True, blank=True)

    otp_verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # =====================================
    # PLATFORM SETTINGS
    # =====================================

    PASSENGER_SERVICE_RATE = Decimal("0.05")

    RIDER_COMMISSION_RATE = Decimal("0.10")

    # =====================================
    # STRING REPRESENTATION
    # =====================================

    def __str__(self):

        return f"{self.booking_id}"

    # =====================================
    # GENERATE BOOKING ID
    # =====================================

    def save(self, *args, **kwargs):

        if not self.booking_id:

            from rideshare.utils.id_generator import generate_booking_id

            booking_id = generate_booking_id()

            while RideBooking.objects.filter(booking_id=booking_id).exists():

                booking_id = generate_booking_id()

            self.booking_id = booking_id

        super().save(*args, **kwargs)

    # =====================================
    # GET BASE RIDE PRICE
    # =====================================

    def get_base_price(self):
        """
        Returns the rider/base price.
        Uses final_price if rider
        negotiated price exists.
        """

        return self.final_price or self.estimated_price

    # =====================================
    # PASSENGER SERVICE FEE
    # =====================================

    def get_passenger_service_charge(self):

        base_price = self.get_base_price()

        total = Decimal(base_price) * self.PASSENGER_SERVICE_RATE
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # =====================================
    # RIDER COMMISSION
    # =====================================

    def get_rider_commission(self):

        base_price = self.get_base_price()

        total = Decimal(base_price) * self.RIDER_COMMISSION_RATE

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # =====================================
    # TOTAL PASSENGER PAYMENT
    # =====================================

    def get_total_price(self):

        base_price = self.get_base_price()

        total = Decimal(base_price) + self.get_passenger_service_charge()

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # =====================================
    # RIDER PAYOUT
    # =====================================

    def get_rider_payout(self):

        base_price = self.get_base_price()

        total = Decimal(base_price) - self.get_rider_commission()

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # =====================================
    # PLATFORM TOTAL EARNING
    # =====================================

    def get_platform_earning(self):

        total = self.get_passenger_service_charge() + self.get_rider_commission()

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


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
        RideBooking, on_delete=models.CASCADE, related_name="responses"
    )

    rider = models.ForeignKey(User, on_delete=models.CASCADE)

    route = models.ForeignKey(DriverRoute, on_delete=models.CASCADE)

    response = models.CharField(max_length=50, choices=RESPONSE_CHOICES)

    updated_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


class RideOTP(models.Model):

    booking = models.OneToOneField(RideBooking, on_delete=models.CASCADE)

    code = models.CharField(max_length=6)

    is_verified = models.BooleanField(default=False)

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)


# =========================================
# payment/models.py
# =========================================


class Payment(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
    ]

    PROVIDER_CHOICES = [
        ("PAYSTACK", "Paystack"),
    ]

    booking = models.OneToOneField(
        RideBooking, on_delete=models.CASCADE, related_name="payment"
    )

    passenger = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments"
    )

    rider = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ride_earnings",
    )

    provider = models.CharField(
        max_length=50, choices=PROVIDER_CHOICES, default="PAYSTACK"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(max_length=10, default="NGN")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")

    payment_reference = models.CharField(max_length=255, unique=True)

    access_code = models.CharField(max_length=255, null=True, blank=True)

    authorization_url = models.URLField(null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)

    gateway_response = models.JSONField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return f"{self.payment_reference} " f"- {self.status}"


class RiderBankAccount(models.Model):

    rider = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="bank_account"
    )

    bank_name = models.CharField(max_length=255)

    bank_code = models.CharField(max_length=20)

    account_number = models.CharField(max_length=20)

    account_name = models.CharField(max_length=255)

    recipient_code = models.CharField(max_length=255)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return f"{self.rider.phone_no} " f"- {self.bank_name}"


class RiderPayout(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    booking = models.OneToOneField("rideshare.RideBooking", on_delete=models.CASCADE)

    rider = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    transfer_reference = models.CharField(max_length=255, unique=True)

    transfer_code = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")

    gateway_response = models.JSONField(null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

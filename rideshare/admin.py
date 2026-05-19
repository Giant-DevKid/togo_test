# from django.contrib import admin
# from .models import DriverRoute, RideBooking, RideBookingResponse

# # Register your models here.


# @admin.register(RideBooking)
# class RideBookingAdmin(admin.ModelAdmin):

#     list_display = (
#         "id",
#         "booking_id",
#         "passenger",
#         "selected_rider",
#         "status",
#         "estimated_price",
#         "created_at",
#     )


# admin.site.register(DriverRoute)
# admin.site.register(RideBookingResponse)


# rideshare/admin.py

from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Vehicle,
    DriverRoute,
    RideBooking,
    RideBookingResponse,
    RideOTP,
    Payment,
    RiderBankAccount,
    RiderPayout,
)

# =========================================================
# GLOBAL ADMIN CONFIG
# =========================================================

admin.site.site_header = "RideShare Admin"
admin.site.site_title = "RideShare Dashboard"
admin.site.index_title = "Platform Monitoring Dashboard"


# =========================================================
# INLINE ADMINS
# =========================================================


class RideBookingResponseInline(admin.TabularInline):

    model = RideBookingResponse

    extra = 0

    readonly_fields = (
        "rider",
        "route",
        "response",
        "updated_price",
        "created_at",
    )

    can_delete = False

    show_change_link = True


class PaymentInline(admin.StackedInline):

    model = Payment

    extra = 0

    readonly_fields = (
        "payment_reference",
        "provider",
        "amount",
        "currency",
        "status",
        "paid_at",
        "authorization_url",
        "created_at",
    )

    can_delete = False


class RideOTPInline(admin.StackedInline):

    model = RideOTP

    extra = 0

    readonly_fields = (
        "code",
        "is_verified",
        "expires_at",
        "created_at",
    )

    can_delete = False


class RiderPayoutInline(admin.StackedInline):

    model = RiderPayout

    extra = 0

    readonly_fields = (
        "amount",
        "transfer_reference",
        "transfer_code",
        "status",
        "paid_at",
        "created_at",
    )

    can_delete = False


# =========================================================
# VEHICLE ADMIN
# =========================================================


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_link",
        "type",
        "brand",
        "plate_no",
        "seat_cap",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__phone_no",
        "plate_no",
        "brand",
    )

    list_filter = (
        "type",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    def user_link(self, obj):

        if not obj.user:
            return "-"

        url = reverse(
            "admin:account_user_change",
            args=[obj.user.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.email,
        )

    user_link.short_description = "Owner"


# =========================================================
# DRIVER ROUTE ADMIN
# =========================================================


@admin.register(DriverRoute)
class DriverRouteAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "driver_link",
        "start_name",
        "end_name",
        "distance_km",
        "duration_minutes",
        "is_active",
        "created_at",
    )

    search_fields = (
        "driver__email",
        "driver__phone_no",
        "start_name",
        "end_name",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "distance_meters",
        "duration_seconds",
        "encoded_polyline",
        "route_geometry",
        "created_at",
    )

    ordering = ("-created_at",)

    def driver_link(self, obj):

        url = reverse(
            "admin:account_user_change",
            args=[obj.driver.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.driver.email,
        )

    driver_link.short_description = "Driver"

    def distance_km(self, obj):

        return f"{round(obj.distance_meters / 1000, 2)} km"

    distance_km.short_description = "Distance"

    def duration_minutes(self, obj):

        return f"{round(obj.duration_seconds / 60)} mins"

    duration_minutes.short_description = "Duration"


# =========================================================
# RIDE BOOKING ADMIN
# =========================================================


@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):

    list_display = (
        "booking_id",
        "passenger_link",
        "selected_rider_link",
        "pickup_name",
        "destination_name",
        "trip_distance",
        "trip_price",
        "status_badge",
        "payment_status",
        "platform_earning",
        "created_at",
    )

    search_fields = (
        "booking_id",
        "passenger__email",
        "passenger__phone_no",
        "selected_rider__email",
        "pickup_name",
        "destination_name",
    )

    list_filter = (
        "status",
        "created_at",
    )

    readonly_fields = (
        "booking_id",
        "estimated_price",
        "distance_meters",
        "encoded_polyline",
        "route_geometry",
        "ride_completion_otp",
        "otp_generated_at",
        "otp_verified_at",
        "created_at",
    )

    inlines = [
        RideBookingResponseInline,
        PaymentInline,
        RideOTPInline,
        RiderPayoutInline,
    ]

    ordering = ("-created_at",)

    actions = [
        "mark_as_confirmed",
        "mark_as_completed",
        "mark_as_cancelled",
    ]

    fieldsets = (
        (
            "Booking Information",
            {
                "fields": (
                    "booking_id",
                    "status",
                    "passenger",
                    "selected_rider",
                )
            },
        ),
        (
            "Trip Information",
            {
                "fields": (
                    "pickup_name",
                    "destination_name",
                    "pickup_lat",
                    "pickup_lng",
                    "destination_lat",
                    "destination_lng",
                    "distance_meters",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "estimated_price",
                    "final_price",
                )
            },
        ),
        (
            "OTP Verification",
            {
                "fields": (
                    "ride_completion_otp",
                    "otp_generated_at",
                    "otp_verified_at",
                )
            },
        ),
        (
            "Route Data",
            {
                "classes": ("collapse",),
                "fields": (
                    "encoded_polyline",
                    "route_geometry",
                ),
            },
        ),
    )

    def passenger_link(self, obj):

        url = reverse(
            "admin:account_user_change",
            args=[obj.passenger.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.passenger.email,
        )

    passenger_link.short_description = "Passenger"

    def selected_rider_link(self, obj):

        if not obj.selected_rider:
            return "-"

        url = reverse(
            "admin:account_user_change",
            args=[obj.selected_rider.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.selected_rider.email,
        )

    selected_rider_link.short_description = "Rider"

    def trip_distance(self, obj):

        return f"{round(obj.distance_meters / 1000, 2)} km"

    trip_distance.short_description = "Distance"

    def trip_price(self, obj):

        return f"₦{obj.get_total_price()}"

    trip_price.short_description = "Total Paid"

    def platform_earning(self, obj):

        return f"₦{obj.get_platform_earning()}"

    platform_earning.short_description = "Platform Earn"

    def payment_status(self, obj):

        if hasattr(obj, "payment"):

            status = obj.payment.status

            colors = {
                "SUCCESS": "green",
                "FAILED": "red",
                "PENDING": "orange",
                "PROCESSING": "blue",
                "REFUNDED": "purple",
            }

            color = colors.get(status, "gray")

            return format_html(
                '<span style="color:white;background:{};padding:4px 10px;border-radius:10px;">{}</span>',
                color,
                status,
            )

        return "-"

    payment_status.short_description = "Payment"

    def status_badge(self, obj):

        colors = {
            "PENDING": "#f39c12",
            "RIDER_SELECTED": "#3498db",
            "PAYMENT_PENDING": "#9b59b6",
            "CONFIRMED": "#2ecc71",
            "IN_PROGRESS": "#1abc9c",
            "OTP_PENDING": "#34495e",
            "COMPLETED": "#27ae60",
            "CANCELLED": "#e74c3c",
        }

        return format_html(
            """
            <span style="
                background:{};
                color:white;
                padding:5px 12px;
                border-radius:20px;
                font-weight:600;
            ">
                {}
            </span>
            """,
            colors.get(obj.status, "#7f8c8d"),
            obj.status,
        )

    status_badge.short_description = "Status"

    # =========================================
    # BULK ACTIONS
    # =========================================

    @admin.action(description="Mark selected bookings as CONFIRMED")
    def mark_as_confirmed(self, request, queryset):

        queryset.update(status="CONFIRMED")

    @admin.action(description="Mark selected bookings as COMPLETED")
    def mark_as_completed(self, request, queryset):

        queryset.update(status="COMPLETED")

    @admin.action(description="Mark selected bookings as CANCELLED")
    def mark_as_cancelled(self, request, queryset):

        queryset.update(status="CANCELLED")


# =========================================================
# BOOKING RESPONSE ADMIN
# =========================================================


@admin.register(RideBookingResponse)
class RideBookingResponseAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "booking",
        "rider",
        "response",
        "updated_price",
        "created_at",
    )

    search_fields = (
        "booking__booking_id",
        "rider__email",
    )

    list_filter = (
        "response",
        "created_at",
    )

    ordering = ("-created_at",)


# =========================================================
# RIDE OTP ADMIN
# =========================================================


@admin.register(RideOTP)
class RideOTPAdmin(admin.ModelAdmin):

    list_display = (
        "booking",
        "code",
        "is_verified",
        "expires_at",
        "created_at",
    )

    search_fields = ("booking__booking_id",)

    list_filter = (
        "is_verified",
        "created_at",
    )

    readonly_fields = ("created_at",)


# =========================================================
# PAYMENT ADMIN
# =========================================================


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "payment_reference",
        "booking_link",
        "passenger_link",
        "rider_link",
        "amount_display",
        "provider",
        "status_badge",
        "paid_at",
        "created_at",
    )

    search_fields = (
        "payment_reference",
        "booking__booking_id",
        "passenger__email",
        "rider__email",
    )

    list_filter = (
        "status",
        "provider",
        "currency",
        "created_at",
    )

    readonly_fields = (
        "gateway_response",
        "metadata",
        "payment_reference",
        "authorization_url",
        "access_code",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    actions = [
        "mark_as_success",
        "mark_as_failed",
    ]

    def booking_link(self, obj):

        url = reverse(
            "admin:rideshare_ridebooking_change",
            args=[obj.booking.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.booking.booking_id,
        )

    booking_link.short_description = "Booking"

    def passenger_link(self, obj):

        url = reverse(
            "admin:account_user_change",
            args=[obj.passenger.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.passenger.email,
        )

    passenger_link.short_description = "Passenger"

    def rider_link(self, obj):

        if not obj.rider:
            return "-"

        url = reverse(
            "admin:account_user_change",
            args=[obj.rider.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.rider.email,
        )

    rider_link.short_description = "Rider"

    def amount_display(self, obj):

        return f"₦{obj.amount}"

    amount_display.short_description = "Amount"

    def status_badge(self, obj):

        colors = {
            "SUCCESS": "green",
            "FAILED": "red",
            "PENDING": "orange",
            "PROCESSING": "blue",
            "CANCELLED": "gray",
            "REFUNDED": "purple",
        }

        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:10px;">{}</span>',
            colors.get(obj.status, "gray"),
            obj.status,
        )

    status_badge.short_description = "Status"

    @admin.action(description="Mark selected payments as SUCCESS")
    def mark_as_success(self, request, queryset):

        queryset.update(status="SUCCESS")

    @admin.action(description="Mark selected payments as FAILED")
    def mark_as_failed(self, request, queryset):

        queryset.update(status="FAILED")


# =========================================================
# RIDER BANK ACCOUNT ADMIN
# =========================================================


@admin.register(RiderBankAccount)
class RiderBankAccountAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "rider_link",
        "bank_name",
        "account_number",
        "account_name",
        "is_verified",
        "created_at",
    )

    search_fields = (
        "rider__email",
        "rider__phone_no",
        "bank_name",
        "account_number",
    )

    list_filter = (
        "is_verified",
        "created_at",
    )

    readonly_fields = (
        "recipient_code",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    actions = [
        "verify_accounts",
    ]

    def rider_link(self, obj):

        url = reverse(
            "admin:account_user_change",
            args=[obj.rider.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.rider.email,
        )

    rider_link.short_description = "Rider"

    @admin.action(description="Verify selected bank accounts")
    def verify_accounts(self, request, queryset):

        queryset.update(is_verified=True)


# =========================================================
# RIDER PAYOUT ADMIN
# =========================================================


@admin.register(RiderPayout)
class RiderPayoutAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "booking_link",
        "rider_link",
        "amount_display",
        "status_badge",
        "paid_at",
        "created_at",
    )

    search_fields = (
        "booking__booking_id",
        "rider__email",
        "transfer_reference",
    )

    list_filter = (
        "status",
        "created_at",
    )

    readonly_fields = (
        "gateway_response",
        "transfer_reference",
        "transfer_code",
        "paid_at",
        "created_at",
    )

    ordering = ("-created_at",)

    actions = [
        "mark_as_success",
        "mark_as_failed",
    ]

    def booking_link(self, obj):

        url = reverse(
            "admin:rideshare_ridebooking_change",
            args=[obj.booking.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.booking.booking_id,
        )

    booking_link.short_description = "Booking"

    def rider_link(self, obj):

        url = reverse(
            "admin:account_user_change",
            args=[obj.rider.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.rider.email,
        )

    rider_link.short_description = "Rider"

    def amount_display(self, obj):

        return f"₦{obj.amount}"

    amount_display.short_description = "Amount"

    def status_badge(self, obj):

        colors = {
            "SUCCESS": "green",
            "FAILED": "red",
            "PENDING": "orange",
        }

        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:10px;">{}</span>',
            colors.get(obj.status, "gray"),
            obj.status,
        )

    status_badge.short_description = "Status"

    @admin.action(description="Mark selected payouts as SUCCESS")
    def mark_as_success(self, request, queryset):

        queryset.update(status="SUCCESS")

    @admin.action(description="Mark selected payouts as FAILED")
    def mark_as_failed(self, request, queryset):

        queryset.update(status="FAILED")

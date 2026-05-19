from django.contrib import admin
from .models import DriverRoute, RideBooking, RideBookingResponse

# Register your models here.

@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "booking_id",
        "passenger",
        "selected_rider",
        "status",
        "estimated_price",
        "created_at",
    )
admin.site.register(DriverRoute)
admin.site.register(RideBookingResponse)
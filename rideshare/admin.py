from django.contrib import admin
from .models import DriverRoute, RideBooking, RideBookingResponse

# Register your models here.

admin.site.register(RideBooking)
admin.site.register(DriverRoute)
admin.site.register(RideBookingResponse)
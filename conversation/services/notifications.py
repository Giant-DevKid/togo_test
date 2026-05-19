# =========================================
# payment/notifications.py
# =========================================

from conversation.services.message_service import send_text


# =========================================
# PASSENGER PAYMENT SUCCESS
# =========================================
def send_passenger_payment_success_message(booking):

    passenger = booking.passenger

    rider = booking.selected_rider

    return send_text(
        passenger.phone_no,
        (
            "✅ Payment Successful\n\n"
            "Your ride has been confirmed.\n\n"
            f"Driver: "
            f"{rider.first_name} "
            f"{rider.last_name}\n"
            f"Phone: "
            f"{rider.phone_no}\n\n"
            f"Pickup: "
            f"{booking.pickup_name}\n"
            f"Destination: "
            f"{booking.destination_name}\n\n"
            f"Final Price: "
            f"₦{booking.final_price}\n\n"
            "You can now call or "
            "chat with your driver. After ride completion, "
            "an otp will be sent to you by the driver for verification. "
            "Kindly provide the otp to the driver."
        ),
    )


# =========================================
# RIDER PAYMENT SUCCESS
# =========================================
def send_rider_payment_success_message(booking):

    passenger = booking.passenger

    rider = booking.selected_rider

    return send_text(
        rider.phone_no,
        (
            "✅ Passenger Completed Payment\n\n"
            "Ride confirmed successfully.\n\n"
            f"Passenger: "
            f"{passenger.first_name} "
            f"{passenger.last_name}\n"
            f"Phone: "
            f"{passenger.phone_no}\n\n"
            f"Pickup: "
            f"{booking.pickup_name}\n"
            f"Destination: "
            f"{booking.destination_name}\n\n"
            f"Final Price: "
            f"₦{booking.final_price}\n\n"
            "You can now call or "
            "chat with the passenger. "
            "After ride completion request and "
            "verify otp using the booking ID: "
            f"{booking.booking_id} to receive your payment"
        ),
    )

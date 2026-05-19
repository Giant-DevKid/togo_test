import requests
import os

from rideshare.models import Payment

def initialize_paystack_payment(
    booking
):

    url = (
        "https://api.paystack.co/transaction/initialize"
    )

    headers = {

        "Authorization": (
            f"Bearer "
            f"{os.getenv("PAYSTACK_SECRET_KEY")}"
        ),

        "Content-Type": "application/json"
    }

    payload = {

        "email": (
            booking.passenger.email
        ),

        "amount": int(
            booking.get_total_price() * 100
        ),

        "callback_url": (
            os.getenv("PAYSTACK_CALLBACK_URL")
        ),

        "metadata": {

            "booking_id": booking.id
        }
    }

    response = requests.post(

        url,

        json=payload,

        headers=headers
    )

    data = response.json()

    payment_data = data["data"]

    payment = Payment.objects.create(

        booking=booking,

        passenger=booking.passenger,

        rider=booking.selected_rider,

        amount=booking.get_total_price(),

        provider="PAYSTACK",

        status="PENDING",

        payment_reference=(
            payment_data["reference"]
        ),

        access_code=(
            payment_data["access_code"]
        ),

        authorization_url=(
            payment_data[
                "authorization_url"
            ]
        ),

        metadata=payload["metadata"]
    )

    return payment


def release_rider_payment(
    booking
):

    payment = booking.payment

    

    print(
        "Release rider payout"
    )
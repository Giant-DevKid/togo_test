import requests
import os

from django.conf import settings


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
            booking.final_price * 100
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

    return data["data"][
        "authorization_url"
    ]
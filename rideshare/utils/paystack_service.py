import requests
import os
import uuid

from decimal import Decimal

from django.utils import timezone

from rideshare.models import RiderPayout, RiderBankAccount, Payment

headers = {"Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}"}


def initialize_paystack_payment(booking):

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": (f"Bearer " f"{os.getenv("PAYSTACK_SECRET_KEY")}"),
        "Content-Type": "application/json",
    }

    payload = {
        "email": (booking.passenger.email),
        "amount": int(booking.get_total_price() * 100),
        "callback_url": (os.getenv("PAYSTACK_CALLBACK_URL")),
        "metadata": {"booking_id": booking.id},
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    payment_data = data["data"]

    payment = Payment.objects.create(
        booking=booking,
        passenger=booking.passenger,
        rider=booking.selected_rider,
        amount=booking.get_total_price(),
        provider="PAYSTACK",
        status="PENDING",
        payment_reference=(payment_data["reference"]),
        access_code=(payment_data["access_code"]),
        authorization_url=(payment_data["authorization_url"]),
        metadata=payload["metadata"],
    )

    return payment


# def verify_account_no(data):
#     url = "https://api.paystack.co/bank/resolve"

#     params = {
#         "account_number": data.get("account_number"),
#         "bank_code": data.get("bank_code"),
#     }
#     response = requests.get(url, headers=headers, params=params)
#     return response.json()


def verify_account_no(data):

    url = "https://api.paystack.co/bank/resolve"

    params = {
        "account_number": (str(data.get("account_number")).strip()),
        "bank_code": (str(data.get("bank_code")).strip()),
    }

    try:

        response = requests.get(url, headers=headers, params=params, timeout=30)

        return response.json()

    except Exception as e:

        return {"status": False, "message": str(e)}


def fetch_banks():

    url = "https://api.paystack.co/bank"

    response = requests.get(url, headers=headers)

    data = response.json()

    if not data.get("status"):

        return []

    return data.get("data", [])


def create_recipient(data):
    url = "https://api.paystack.co/transferrecipient"

    data = {
        "account_number": data.get("account_number"),
        "bank_code": data.get("bank_code"),
        "name": data.get("account_name"),
        "currency": "NGN",
        "type": "nuban",
    }

    response2 = requests.post(url, headers=headers, data=data)

    return response2.json()


def get_bank_by_name(bank_name):

    banks = fetch_banks()

    normalized_bank = bank_name.strip().lower()

    for bank in banks:

        bank_display_name = bank.get("name", "").strip().lower()

        if normalized_bank in bank_display_name:

            return {"name": bank.get("name"), "code": bank.get("code")}

    return None


def make_payment_to_rider(data):
    url = "https://api.paystack.co/transfer"

    data = {
        "source": "balance",
        "amount": data.get("amount"),
        "reference": data.get("reference"),
        "recipient": data.get("recipient"),
        "reason": data.get("reason"),
    }
    response = requests.post(url, headers=headers, data=data)

    return response.json()


def release_rider_payment(booking):

    bank_account = RiderBankAccount.objects.filter(rider=booking.selected_rider).first()

    if not bank_account:

        return False

    payout_amount = Decimal(booking.final_price) * Decimal("0.95")

    reference = f"PAYOUT-{uuid.uuid4().hex[:10]}"

    payout = RiderPayout.objects.create(
        booking=booking,
        rider=booking.selected_rider,
        amount=payout_amount,
        transfer_reference=reference,
    )

    response = make_payment_to_rider(
        {
            "amount": int(payout_amount * 100),
            "reference": reference,
            "recipient": (bank_account.recipient_code),
            "reason": (f"Ride payout " f"{booking.booking_id}"),
        }
    )

    payout.gateway_response = response

    if response.get("status"):

        payout.status = "SUCCESS"

        payout.transfer_code = response["data"].get("transfer_code")

        payout.paid_at = timezone.now()
    else:

        payout.status = "FAILED"

    payout.save()

    return payout

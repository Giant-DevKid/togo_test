import requests
import os
import json
from whatsapp.services import send_whatsapp_message, send_whatsapp_image

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
BASE_URL = f"https://graph.facebook.com/v22.0/" f"{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json",
}


def send_whatsapp_payload(payload):

    url = "https://graph.facebook.com/v22.0/" f"{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, headers=headers, json=payload)

    print("\n========== PAYLOAD ==========")
    print(payload)

    print("\n========== RESPONSE ==========")
    print(response.status_code)
    print(response.text)

    return response.json()


def send_text(phone_number, message):

    return send_whatsapp_message(phone_number, message)


def send_image(phone_number, image_url, caption=None):

    return send_whatsapp_image(to=phone_number, image_url=image_url, caption=caption)


# =========================================
# SEND BUTTONS
# =========================================
def send_buttons(phone_number, body_text, buttons):
    """
    buttons format:

    [
        {
            "id": "create_vehicle",
            "title": "Add Vehicle"
        }
    ]
    """

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"]}}
                    for btn in buttons
                ]
            },
        },
    }

    response = requests.post(
        BASE_URL,
        headers=headers,
        json=payload,
    )

    print("\n========== BUTTON PAYLOAD ==========")
    print(json.dumps(payload, indent=2))

    print("\n========== BUTTON RESPONSE ==========")
    print("STATUS:", response.status_code)
    print(response.text)

    return response.json()


# =========================================
# SEND LIST MESSAGE
# =========================================
def send_list_message(phone_number, body_text, button_text, sections):

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {"button": button_text, "sections": sections},
        },
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.json()

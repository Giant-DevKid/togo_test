import requests
import os
from whatsapp.services import send_whatsapp_message, send_whatsapp_image

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


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


def send_button_message(phone_number, body, buttons, header=None, footer=None):

    formatted_buttons = []

    for index, button in enumerate(buttons, start=1):

        formatted_buttons.append(
            {"type": "reply", "reply": {"id": button["id"], "title": button["title"]}}
        )

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": (formatted_buttons)},
        },
    }

    # =====================================
    # OPTIONAL HEADER
    # =====================================

    if header:

        payload["interactive"]["header"] = {"type": "text", "text": header}

    # =====================================
    # OPTIONAL FOOTER
    # =====================================

    if footer:

        payload["interactive"]["footer"] = {"text": footer}

    return send_whatsapp_payload(payload)

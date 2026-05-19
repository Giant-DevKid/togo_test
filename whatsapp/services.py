import requests
import os
import json

ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


BASE_URL = f"https://graph.facebook.com/v22.0/" f"{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def send_whatsapp_message(to, message):

    url = f"https://graph.facebook.com/v22.0/" f"{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": (f"Bearer {ACCESS_TOKEN}"),
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": message},
    }

    print("\n========== TEXT PAYLOAD ==========")
    print(json.dumps(payload, indent=2))

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    print("\n========== TEXT RESPONSE ==========")
    print("STATUS:", response.status_code)
    print(response.text)

    return response.json()


def send_whatsapp_buttons(to, body_text, buttons):

    url = f"https://graph.facebook.com/v22.0/" f"{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": (f"Bearer {ACCESS_TOKEN}"),
        "Content-Type": "application/json",
    }

    formatted_buttons = []

    for button in buttons:

        formatted_buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": str(button["id"])[:256],
                    "title": str(button["title"])[:20],
                },
            }
        )

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text[:1024]},
            "action": {"buttons": formatted_buttons},
        },
    }

    print("\n========== BUTTON PAYLOAD ==========")
    print(json.dumps(payload, indent=2))

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    print("\n========== BUTTON RESPONSE ==========")
    print("STATUS:", response.status_code)
    print(response.text)

    return response.json()


def send_interactive_buttons_message(to, body, buttons, footer=None):
    """
    buttons format:

    [
        {
            "id": "book_ride",
            "title": "Book Ride"
        },
        {
            "id": "support",
            "title": "Support"
        }
    ]
    """

    interactive_buttons = []

    for button in buttons:

        interactive_buttons.append(
            {
                "type": "reply",
                "reply": {"id": button["id"], "title": button["title"][:20]},
            }
        )

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": interactive_buttons},
        },
    }

    if footer:

        payload["interactive"]["footer"] = {"text": footer}

    response = requests.post(BASE_URL, headers=HEADERS, json=payload)

    return response.json()


def send_list_message(to, body, button_text, sections, footer=None):
    """
    sections format:

    [
        {
            "title": "Main Menu",
            "rows": [
                {
                    "id": "book_ride",
                    "title": "Book Ride",
                    "description": "Book a new ride"
                }
            ]
        }
    ]
    """

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {"button": button_text, "sections": sections},
        },
    }

    if footer:

        payload["interactive"]["footer"] = {"text": footer}

    response = requests.post(BASE_URL, headers=HEADERS, json=payload)

    return response.json()


def send_message_with_menu(
    phone_number,
    message,
    menu_body,
    buttons,
):

    send_whatsapp_message(phone_number, message)

    return send_whatsapp_buttons(to=phone_number, body_text=menu_body, buttons=buttons)


def send_whatsapp_image(to, image_url, caption=None):

    url = f"https://graph.facebook.com/v23.0/" f"{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url},
    }

    # =====================================
    # OPTIONAL CAPTION
    # =====================================

    if caption:

        payload["image"]["caption"] = caption

    response = requests.post(url, headers=headers, json=payload)

    print("WHATSAPP IMAGE RESPONSE:", response.text)

    return response.json()

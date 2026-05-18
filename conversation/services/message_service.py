from whatsapp.services import (
    send_whatsapp_message,
    send_whatsapp_image
)


def send_text(
    phone_number,
    message
):

    return send_whatsapp_message(
        phone_number,
        message
    )

def send_image(
    phone_number,
    image_url,
    caption=None
):

    return send_whatsapp_image(

        to=phone_number,

        image_url=image_url,

        caption=caption
    )
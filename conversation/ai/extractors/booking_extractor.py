from conversation.ai.client import (
    ask_ai_json
)

from conversation.ai.prompts.booking_prompt import (
    BOOKING_EXTRACTION_PROMPT
)


def extract_booking_data(message):

    return ask_ai_json(

        BOOKING_EXTRACTION_PROMPT,

        message
    )

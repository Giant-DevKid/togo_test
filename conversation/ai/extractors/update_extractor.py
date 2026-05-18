from conversation.ai.client import (
    ask_ai_json
)

from conversation.ai.prompts.booking_prompt import (
    UPDATE_BOOKING_PROMPT
)


def extract_update_data(message):

    return ask_ai_json(

        UPDATE_BOOKING_PROMPT,

        message
    )
from conversation.ai.client import (
    ask_ai_json
)

from conversation.ai.prompts.booking_prompt import (
    BOOKING_ACTION_PROMPT
)


def extract_booking_action(
    message
):

    return ask_ai_json(

        BOOKING_ACTION_PROMPT,

        message
    )
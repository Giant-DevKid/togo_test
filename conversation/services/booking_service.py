from conversation.ai.client import ask_ai

from conversation.ai.prompts.booking_prompt import BOOKING_ACTION_PROMPT


# =========================================
# EXTRACT RIDER BOOKING ACTION
# =========================================
def extract_booking_action(message):

    response = ask_ai(BOOKING_ACTION_PROMPT, message)

    if not response:

        return {}

    return response

from conversation.ai.client import ask_ai_json

from conversation.ai.prompts.ride_completion_prompt import RIDE_COMPLETION_PROMPT


def extract_ride_completion_data(message):

    response = ask_ai_json(RIDE_COMPLETION_PROMPT, message)

    return {
        "action": response.get("action"),
        "booking_id": response.get("booking_id"),
        "otp": response.get("otp"),
    }

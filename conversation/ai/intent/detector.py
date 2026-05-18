from conversation.ai.client import (
    ask_ai_json
)

from conversation.ai.prompts.common_prompts import (
    INTENT_PROMPT
)


def detect_intent(message):

    response = ask_ai_json(

        INTENT_PROMPT,

        message
    )

    return response.get(
        "intent",
        "UNKNOWN"
    )
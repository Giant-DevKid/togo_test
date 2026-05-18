from conversation.ai.client import (
    ask_ai_json
)

from conversation.ai.prompts.vehicle_prompts import (
    VEHICLE_TYPE_PROMPT
)


def extract_vehicle_type(
    message
):

    response = ask_ai_json(

        VEHICLE_TYPE_PROMPT,

        message
    )

    return response.get(
        "vehicle_type"
    )
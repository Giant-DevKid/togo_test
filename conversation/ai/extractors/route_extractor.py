from conversation.ai.client import (
    ask_ai_json
)

from conversation.ai.prompts.route_prompts import (
    CREATE_ROUTE_PROMPT
)


def extract_route_data(message):

    return ask_ai_json(

        CREATE_ROUTE_PROMPT,

        message
    )
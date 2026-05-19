from conversation.ai.client import ask_ai_json

from conversation.ai.prompts.onboarding_prompts import ROLE_CLASSIFICATION_PROMPT


def extract_user_role(message):

    response = ask_ai_json(ROLE_CLASSIFICATION_PROMPT, message)

    return response.get("role", "unknown")

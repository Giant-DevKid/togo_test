from conversation.ai.client import ask_ai

from conversation.ai.prompts.onboarding_prompts import WELCOME_PROMPT

ROLE_CAPABILITIES = {
    "passenger": ["Book rides", "Track rides", "Manage bookings"],
    "rider": ["Create routes", "Accept ride requests", "Manage trips"],
    "event_organiser": ["Create events", "Manage attendees", "Handle bookings"],
    "tour_guide": ["Create tours", "Manage tour schedules", "Receive bookings"],
}


def generate_welcome_message(user, is_returning=False):

    capabilities = ROLE_CAPABILITIES.get(user.user_type, [])

    prompt = f"""

    Name: {user.first_name}

    Role: {user.user_type}

    Returning User: {is_returning}

    Features:
    {', '.join(capabilities)}

    """

    return ask_ai(WELCOME_PROMPT, prompt)

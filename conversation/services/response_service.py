def get_user_capabilities(user_type):

    capabilities = {
        "passenger": ["Book rides", "Manage bookings", "Track trips"],
        "rider": ["Create routes", "Manage vehicle profile", "Accept ride requests"],
        "event_organiser": [
            "Create events",
            "Manage event bookings",
            "Track attendees",
        ],
        "tour_guide": ["Create tours", "Manage tour schedules", "Handle tour bookings"],
    }

    return capabilities.get(user_type, [])


def build_fallback_response(user):

    capabilities = get_user_capabilities(user.user_type)

    capability_text = "\n".join([f"• {item}" for item in capabilities])

    role_name = user.user_type.replace("_", " ").title()

    return (
        f"Hi {user.first_name} 👋\n\n"
        f"You're currently using "
        f"Togo Mobility as a "
        f"{role_name}.\n\n"
        f"Here’s what I can help "
        f"you with:\n\n"
        f"{capability_text}\n\n"
        "Just send a message "
        "telling me what you'd "
        "like to do 😊"
    )

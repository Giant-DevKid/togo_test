from conversation.registries.state_registry import (
    STATE_REGISTRY
)

from conversation.handlers.onboarding import (
    handle_start
)


GLOBAL_COMMANDS = [
    "menu",
    "home",
    "start",
]


def route_message(
    session,
    message
):

    if message.lower() in GLOBAL_COMMANDS:

        return handle_start(
            session,
            message
        )

    handler = STATE_REGISTRY.get(
        session.state
    )

    if not handler:

        return handle_start(
            session,
            message
        )

    return handler(
        session,
        message
    )

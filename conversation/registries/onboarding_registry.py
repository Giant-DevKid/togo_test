
from conversation.constants import *

from conversation.handlers.onboarding import (
    handle_start,
    handle_main_role,
    handle_service_provider_role,
    handle_first_name,
    handle_last_name,
    handle_email,
    handle_otp,
)

ONBOARDING_STATES = {

    START:
        handle_start,

    ASK_MAIN_ROLE:
        handle_main_role,

    ASK_SERVICE_PROVIDER_ROLE:
        handle_service_provider_role,

    ASK_FIRST_NAME:
        handle_first_name,

    ASK_LAST_NAME:
        handle_last_name,

    ASK_EMAIL:
        handle_email,

    VERIFY_OTP:
        handle_otp,
}
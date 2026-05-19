from django.core.exceptions import ValidationError

from conversation.ai.extractors.role_extractor import extract_user_role

from conversation.ai.generators.welcome_generator import generate_welcome_message

from conversation.services.message_service import send_text, send_image

from conversation.state.onboarding_steps import (
    ONBOARDING_FLOW,
    ASK_ROLE,
    ASK_FIRST_NAME,
    ASK_LAST_NAME,
    ASK_EMAIL,
    VERIFY_OTP,
)

from account.services import create_user_account, send_verification_otp, verify_user_otp

SUPPORTED_ROLES = [
    "passenger", 
    "rider", 
    "event_organiser", 
    "tour_guide"
    ]

WELCOME_IMAGE_URL = "https://i.pravatar.cc/100"


def start_onboarding_flow(session):

    # =====================================
    # VERIFIED RETURNING USER
    # =====================================

    if session.user and session.user.is_verified:

        welcome_message = generate_welcome_message(session.user, is_returning=True)

        return send_text(session.phone_number, welcome_message)

    # =====================================
    # INITIALIZE FLOW
    # =====================================

    session.context = {"active_flow": ONBOARDING_FLOW, "step": ASK_ROLE, "data": {}}

    session.save()

    # =====================================
    # SEND WELCOME IMAGE COMING SOON
    # =====================================

    send_image(

        session.phone_number,

        WELCOME_IMAGE_URL,

        (
            "Welcome to Togo Mobility 🚗"
        )
    )

    # =====================================
    # SEND INTRO MESSAGE
    # =====================================

    return send_text(
        session.phone_number,
        (
            "Welcome to Togo Mobility 🚗\n\n"
            "Your all-in-one mobility "
            "and experience platform.\n\n"
            "With Togo Mobility you can:\n\n"
            "• Book rides\n"
            "• Become a driver\n"
            "• Organize events\n"
            "• Create tours\n"
            "• Connect with travelers and commuters\n\n"
            "Let’s get you started 😊\n\n"
            "Are you registering as:\n\n"
            "• Passenger\n"
            "• Driver\n"
            "• Event Organizer\n"
            "• Tour Guide\n\n"
            "Just tell me what you'd like to do."
        ),
    )


# =========================================
# MAIN FLOW HANDLER
# =========================================
def handle_onboarding_flow(session, message):

    step = session.context.get("step")

    if step == ASK_ROLE:

        return handle_role_step(session, message)

    if step == ASK_FIRST_NAME:

        return handle_first_name_step(session, message)

    if step == ASK_LAST_NAME:

        return handle_last_name_step(session, message)

    if step == ASK_EMAIL:

        return handle_email_step(session, message)

    if step == VERIFY_OTP:

        return handle_otp_step(session, message)


# =========================================
# HANDLE ROLE
# =========================================
def handle_role_step(session, message):

    role = extract_user_role(message)

    if role not in SUPPORTED_ROLES:

        return send_text(
            session.phone_number,
            (
                "I couldn't understand the role.\n\n"
                "Please choose one:\n"
                "- Passenger\n"
                "- Rider\n"
                "- Event Organiser\n"
                "- Tour Guide"
            ),
        )

    session.context = {
        "active_flow": ONBOARDING_FLOW,
        "step": ASK_FIRST_NAME,
        "data": {"user_type": role},
    }

    session.save()

    return send_text(session.phone_number, "Great 🎉\n\nWhat's your first name?")


# =========================================
# HANDLE FIRST NAME
# =========================================
def handle_first_name_step(session, message):

    session.context["data"]["first_name"] = message.strip()

    session.context["step"] = ASK_LAST_NAME

    session.save()

    return send_text(session.phone_number, "Nice 😊\n\nWhat's your last name?")


# =========================================
# HANDLE LAST NAME
# =========================================
def handle_last_name_step(session, message):

    session.context["data"]["last_name"] = message.strip()

    session.context["step"] = ASK_EMAIL

    session.save()

    return send_text(session.phone_number, "Perfect 👍\n\nEnter your email address")


# =========================================
# HANDLE EMAIL
# =========================================
def handle_email_step(session, message):

    email = message.strip().lower()

    data = session.context.get("data", {})

    try:

        user = create_user_account(
            email=email, user_type=data.get("user_type"), phone_no=session.phone_number
        )

    except ValidationError as e:

        return send_text(session.phone_number, str(e))

    user.first_name = data.get("first_name")

    user.last_name = data.get("last_name")

    user.save()

    try:

        send_verification_otp(user)

    except Exception:

        return send_text(
            session.phone_number,
            ("Unable to send OTP right now.\n" "Please try again later."),
        )

    session.user = user

    session.context["step"] = VERIFY_OTP

    session.save()

    return send_text(
        session.phone_number,
        (
            "OTP has been sent to your email 📩\n\n"
            "Enter the OTP to verify your account"
        ),
    )


# =========================================
# HANDLE OTP
# =========================================
def handle_otp_step(session, message):

    success, response_message = verify_user_otp(session.user, message)

    if not success:

        return send_text(session.phone_number, response_message)

    session.user.is_verified = True

    session.user.save()

    session.context = {"active_flow": None, "step": None, "data": {}}

    session.save()

    welcome_message = generate_welcome_message(session.user, is_returning=False)

    return send_text(session.phone_number, welcome_message)

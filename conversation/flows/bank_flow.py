from rideshare.models import RiderBankAccount

from rideshare.utils.paystack_service import (
    verify_account_no,
    create_recipient,
    get_bank_by_name,
)

from conversation.services.message_service import send_text

from conversation.state.bank_steps import *

# =========================================
# START FLOW
# =========================================


def start_bank_flow(session):

    session.context = {"active_flow": BANK_FLOW, "step": ASK_BANK_NAME, "data": {}}

    session.save()

    return send_text(
        session.phone_number,
        ("🏦 Add Bank Account\n\n" "Enter your bank name.\n\n" "Example:\n" "Opay"),
    )


# =========================================
# HANDLE FLOW
# =========================================


def handle_bank_flow(session, message):

    step = session.context.get("step")

    if step == ASK_BANK_NAME:

        return handle_bank_name(session, message)

    if step == ASK_ACCOUNT_NUMBER:

        return handle_account_number(session, message)


# =========================================
# HANDLE BANK NAME
# =========================================


def handle_bank_name(session, message):

    bank_name = message.strip()

    bank_data = get_bank_by_name(bank_name)

    if not bank_data:

        return send_text(
            session.phone_number,
            ("Bank not found.\n\n" "Please enter a valid " "bank name."),
        )

    bank_code = bank_data["code"]

    bank_name = bank_data["name"]

    session.context["data"] = {"bank_name": bank_name, "bank_code": bank_code}

    session.context["step"] = ASK_ACCOUNT_NUMBER

    session.save()

    return send_text(session.phone_number, "Enter account number.")


# =========================================
# HANDLE ACCOUNT NUMBER
# =========================================


def handle_account_number(session, message):

    account_number = message.strip()

    data = session.context.get("data", {})

    response = verify_account_no(
        {"account_number": (account_number), "bank_code": (data["bank_code"])}
    )

    if not response.get("status"):

        return send_text(session.phone_number, (f"Unable to verify account.\n\n"))

    account_data = response.get("data", {})

    account_name = account_data.get("account_name")

    recipient_response = create_recipient(
        {
            "account_number": (account_number),
            "bank_code": (data["bank_code"]),
            "account_name": (account_name),
        }
    )

    if not recipient_response.get("status"):

        return send_text(
            session.phone_number, ("Unable to create " "transfer recipient.")
        )

    recipient_data = recipient_response.get("data", {})

    RiderBankAccount.objects.update_or_create(
        rider=session.user,
        defaults={
            "bank_name": (data["bank_name"]),
            "bank_code": (data["bank_code"]),
            "account_number": (account_number),
            "account_name": (account_name),
            "recipient_code": (recipient_data.get("recipient_code")),
            "is_verified": True,
        },
    )

    session.context = {"active_flow": None, "step": None, "data": {}}

    session.save()

    return send_text(
        session.phone_number,
        (
            "✅ Bank account added\n\n"
            f"Bank: "
            f"{data['bank_name'].title()}\n"
            f"Account Name: "
            f"{account_name}"
        ),
    )


# =========================================
# VIEW BANK ACCOUNT
# =========================================


def view_bank_account(session):

    bank_account = RiderBankAccount.objects.filter(rider=session.user).first()

    if not bank_account:

        return send_text(
            session.phone_number,
            (
                "You have not added "
                "a bank account yet.\n\n"
                "Say:\n"
                "• add bank account"
            ),
        )

    masked_account = f"******" f"{bank_account.account_number[-4:]}"

    return send_text(
        session.phone_number,
        (
            "🏦 Your Bank Account\n\n"
            f"Bank: "
            f"{bank_account.bank_name.title()}\n"
            f"Account Name: "
            f"{bank_account.account_name}\n"
            f"Account Number: "
            f"{masked_account}\n\n"
            "Say:\n"
            "• update bank account"
        ),
    )


# =========================================
# START UPDATE FLOW
# =========================================


def start_update_bank_flow(session):

    bank_account = RiderBankAccount.objects.filter(rider=session.user).first()

    if not bank_account:

        return send_text(
            session.phone_number,
            ("No bank account found.\n\n" "Say:\n" "• add bank account"),
        )

    session.context = {
        "active_flow": (BANK_UPDATE_FLOW),
        "step": (CONFIRM_BANK_UPDATE),
        "data": {},
    }

    session.save()

    return send_text(
        session.phone_number,
        (
            "⚠️ You are about to "
            "replace your payout bank.\n\n"
            "Reply:\n"
            "• yes\n"
            "• no"
        ),
    )


# =========================================
# HANDLE UPDATE CONFIRMATION
# =========================================


def handle_update_confirmation(session, message):

    normalized_message = message.strip().lower()

    if normalized_message in ["no", "cancel"]:

        session.context = {"active_flow": None, "step": None, "data": {}}

        session.save()

        return send_text(session.phone_number, "Bank update cancelled.")

    if normalized_message != "yes":

        return send_text(session.phone_number, ("Reply with:\n\n" "• Yes\n" "• No"))

    # =====================================
    # START NEW BANK FLOW
    # =====================================

    session.context = {"active_flow": BANK_FLOW, "step": ASK_BANK_NAME, "data": {}}

    session.save()

    return send_text(
        session.phone_number, ("Enter your new bank name.\n\n" "Example:\n" "Opay")
    )


def handle_bank_flow(session, message):

    active_flow = session.context.get("active_flow")

    step = session.context.get("step")

    # =====================================
    # UPDATE FLOW
    # =====================================

    if active_flow == BANK_UPDATE_FLOW:

        if step == CONFIRM_BANK_UPDATE:

            return handle_update_confirmation(session, message)

    # =====================================
    # ADD BANK FLOW
    # =====================================

    if step == ASK_BANK_NAME:

        return handle_bank_name(session, message)

    if step == ASK_ACCOUNT_NUMBER:

        return handle_account_number(session, message)

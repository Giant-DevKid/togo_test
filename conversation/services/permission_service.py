from conversation.permissions import ROLE_PERMISSIONS


def can_access_intent(user, intent):

    if not user:

        return False

    # print("USER TYPE:", user.user_type)
    # print("INTENT:", intent)

    allowed = ROLE_PERMISSIONS.get(user.user_type, [])

    return intent in allowed

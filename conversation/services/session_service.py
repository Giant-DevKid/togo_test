def initialize_session_context(session):

    if not session.context:

        session.context = {}

    if "active_flow" not in session.context:

        session.context["active_flow"] = None

    if "step" not in session.context:

        session.context["step"] = None

    if "data" not in session.context:

        session.context["data"] = {}

    session.save()


def reset_session(session):

    session.context = {"active_flow": None, "step": None, "data": {}}

    session.save()

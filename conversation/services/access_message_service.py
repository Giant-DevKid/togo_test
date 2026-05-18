def get_access_denied_message(
    user,
    intent
):

    role = user.user_type

    # =====================================
    # PASSENGER
    # =====================================

    if role == "passenger":

        if intent in [

            "CREATE_ROUTE",

            "VIEW_ROUTES",

            "UPDATE_ROUTE",

            "DELETE_ROUTE",

            "CREATE_VEHICLE",

            "UPDATE_VEHICLE",

            "VIEW_VEHICLE",

            "VIEW_RIDE_REQUESTS",

            "ACCEPT_BOOKING",

            "REJECT_BOOKING"
        ]:

            return (

                "🚗 These features are "
                "only available for riders.\n\n"

                "As a passenger you can:\n"

                "• Book rides\n"

                "• Update bookings\n"

                "• Cancel bookings\n"

                "• View your rides"
            )

    # =====================================
    # RIDER
    # =====================================

    if role == "rider":

        if intent in [

            "BOOK_RIDE",

            "UPDATE_BOOKING",

            "CANCEL_BOOKING"
        ]:

            return (

                "😊 Ride booking is "
                "only available for passengers.\n\n"

                "As a rider you can:\n"

                "• Create routes\n"

                "• Manage routes\n"

                "• Manage vehicles\n"

                "• Receive ride requests"
            )

    return (

        "You do not have access "
        "to this feature."
    )
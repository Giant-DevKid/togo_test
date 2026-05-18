# import os

# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse

# from rest_framework.decorators import api_view
# from rest_framework.response import Response

# from conversation.models import (
#     ConversationSession
# )

# from account.services import (
#     get_existing_user
# )

# from conversation.ai.handlers.ai_router import (
#     route_ai_message
# )


# VERIFY_TOKEN = os.getenv(
#     "WHATSAPP_VERIFY_TOKEN"
# )


# @csrf_exempt
# @api_view(["GET", "POST"])
# def whatsapp_webhook(request):

#     # =====================================
#     # VERIFY WEBHOOK
#     # =====================================

#     if request.method == "GET":

#         mode = request.GET.get(
#             "hub.mode"
#         )

#         token = request.GET.get(
#             "hub.verify_token"
#         )

#         challenge = request.GET.get(
#             "hub.challenge"
#         )

#         if (
#             mode == "subscribe"
#             and token == VERIFY_TOKEN
#         ):

#             return HttpResponse(
#                 challenge,
#                 content_type="text/plain"
#             )

#         return HttpResponse(
#             "Verification failed",
#             status=403
#         )

#     # =====================================
#     # RECEIVE WHATSAPP EVENTS
#     # =====================================

#     elif request.method == "POST":

#         print("AI WEBHOOK HIT")

#         try:

#             print(
#                 "REQUEST DATA:",
#                 request.data
#             )

#             entry = request.data[
#                 "entry"
#             ][0]

#             changes = entry[
#                 "changes"
#             ][0]

#             value = changes[
#                 "value"
#             ]

#             messages = value.get(
#                 "messages"
#             )

#             if not messages:

#                 return Response({
#                     "status":
#                         "no messages"
#                 })

#             message_data = messages[0]

#             phone_number = (
#                 message_data["from"]
#             )

#             message_type = (
#                 message_data["type"]
#             )

#             # =================================
#             # TEXT MESSAGE
#             # =================================

#             if message_type == "text":

#                 message_text = (
#                     message_data
#                     ["text"]["body"]
#                 )

#             # =================================
#             # INTERACTIVE MESSAGE
#             # =================================

#             elif (
#                 message_type
#                 == "interactive"
#             ):

#                 interactive = (
#                     message_data[
#                         "interactive"
#                     ]
#                 )

#                 interactive_type = (
#                     interactive.get(
#                         "type"
#                     )
#                 )

#                 # =============================
#                 # BUTTON REPLY
#                 # =============================

#                 if (
#                     interactive_type
#                     == "button_reply"
#                 ):

#                     message_text = (
#                         interactive[
#                             "button_reply"
#                         ]["id"]
#                     )

#                 # =============================
#                 # LIST REPLY
#                 # =============================

#                 elif (
#                     interactive_type
#                     == "list_reply"
#                 ):

#                     message_text = (
#                         interactive[
#                             "list_reply"
#                         ]["id"]
#                     )

#                 else:

#                     return Response({
#                         "status":
#                             "unsupported interactive type"
#                     })

#             else:

#                 return Response({
#                     "status":
#                         "unsupported message type"
#                 })

#             print(
#                 "AI MESSAGE:",
#                 message_text
#             )

#             # =================================
#             # CREATE SESSION
#             # =================================

#             session, created = (
#                 ConversationSession.objects
#                 .get_or_create(
#                     phone_number=phone_number,
#                     defaults={
#                         "state":
#                             "AI_START"
#                     }
#                 )
#             )

#             # =================================
#             # ATTACH EXISTING USER
#             # =================================

#             existing_user = (
#                 get_existing_user(
#                     phone_number
#                 )
#             )

#             if existing_user:

#                 session.user = (
#                     existing_user
#                 )

#                 session.save()

#             # =================================
#             # INITIALIZE AI CONTEXT
#             # =================================

#             if (
#                 "ai_history"
#                 not in session.context
#             ):

#                 session.context[
#                     "ai_history"
#                 ] = []

#             if (
#                 "active_ai_flow"
#                 not in session.context
#             ):

#                 session.context[
#                     "active_ai_flow"
#                 ] = None

#             session.save()

#             # =================================
#             # ROUTE AI MESSAGE
#             # =================================

#             route_ai_message(
#                 session,
#                 message_text
#             )

#             return Response({
#                 "status": "success"
#             })

#         except Exception as e:

#             print(
#                 "AI WEBHOOK ERROR:",
#                 str(e)
#             )

#             return Response({

#                 "error": str(e)

#             }, status=500)


import os

from django.http import (
    HttpResponse
)

from django.views.decorators.csrf import (
    csrf_exempt
)

from rest_framework.decorators import (
    api_view
)

from rest_framework.response import (
    Response
)

from account.services import (
    get_existing_user
)

from conversation.models import (
    ConversationSession
)

from conversation.router.message_router import (
    route_message
)

from conversation.services.session_service import (
    initialize_session_context
)


VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN"
)


@csrf_exempt
@api_view(["GET", "POST"])
def whatsapp_webhook(request):

    # =====================================
    # VERIFY WEBHOOK
    # =====================================

    if request.method == "GET":

        mode = request.GET.get(
            "hub.mode"
        )

        token = request.GET.get(
            "hub.verify_token"
        )

        challenge = request.GET.get(
            "hub.challenge"
        )

        if (
            mode == "subscribe"
            and token == VERIFY_TOKEN
        ):

            return HttpResponse(
                challenge,
                content_type="text/plain"
            )

        return HttpResponse(
            "Verification failed",
            status=403
        )

    # =====================================
    # RECEIVE EVENTS
    # =====================================

    elif request.method == "POST":

        try:

            entry = request.data[
                "entry"
            ][0]

            changes = entry[
                "changes"
            ][0]

            value = changes[
                "value"
            ]

            messages = value.get(
                "messages"
            )

            if not messages:

                return Response({
                    "status":
                        "no messages"
                })

            message_data = messages[0]

            phone_number = (
                message_data["from"]
            )

            message_type = (
                message_data["type"]
            )

            # =================================
            # TEXT
            # =================================

            if message_type == "text":

                message_text = (
                    message_data
                    ["text"]["body"]
                )

            else:

                return Response({
                    "status":
                        "unsupported type"
                })

            # =================================
            # SESSION
            # =================================

            session, created = (
                ConversationSession.objects
                .get_or_create(
                    phone_number=phone_number
                )
            )

            # =================================
            # ATTACH USER
            # =================================

            existing_user = (
                get_existing_user(
                    phone_number
                )
            )

            if existing_user:

                session.user = (
                    existing_user
                )

                session.save()

            # =================================
            # INITIALIZE CONTEXT
            # =================================

            initialize_session_context(
                session
            )

            # =================================
            # ROUTE MESSAGE
            # =================================

            route_message(

                session,

                message_text
            )

            return Response({
                "status": "success"
            })

        except Exception as e:

            print(
                "WEBHOOK ERROR:",
                str(e)
            )

            return Response({

                "error": str(e)

            }, status=500)
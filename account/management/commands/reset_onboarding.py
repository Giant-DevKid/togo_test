# users/management/commands/reset_onboarding.py

from django.core.management.base import BaseCommand

from account.models import User
from conversation.models import ConversationSession


class Command(BaseCommand):

    help = "Reset onboarding data"

    def add_arguments(self, parser):

        parser.add_argument("--phone", type=str, help="Phone number to reset")

        parser.add_argument(
            "--all", action="store_true", help="Delete all onboarding data"
        )

    def handle(self, *args, **options):

        phone = options.get("phone")
        delete_all = options.get("all")

        if delete_all:

            conversation_count = ConversationSession.objects.all().delete()

            user_count = User.objects.all().delete()

            self.stdout.write(
                self.style.SUCCESS("All onboarding data deleted successfully.")
            )

            return

        if not phone:

            self.stdout.write(self.style.ERROR("Provide --phone or use --all"))

            return

        ConversationSession.objects.filter(phone_number=phone).delete()

        User.objects.filter(phone_no=phone).delete()

        self.stdout.write(
            self.style.SUCCESS(f"Onboarding reset successful for {phone}")
        )

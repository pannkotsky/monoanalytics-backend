from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from profiles.models import Account
from statement.import_utils import import_statement


class Command(BaseCommand):
    help = "Import statement for user accounts"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("--from-date", type=str)
        parser.add_argument("--to-date", type=str)

    def handle(self, *args, **options):
        accounts = Account.objects.filter(profile__user_id=options["user_id"])
        from_date = options["from_date"] and timezone.make_aware(
            datetime.fromisoformat(options["from_date"])
        )
        to_date = options["to_date"] and timezone.make_aware(
            datetime.fromisoformat(options["to_date"])
        )
        for index, account in enumerate(accounts, start=1):
            self.stdout.write(
                self.style.WARNING(
                    f"Importing statement for account {index}/{len(accounts)}"
                )
            )
            try:
                import_statement(account, from_date, to_date)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
        self.stdout.write(self.style.SUCCESS("Statement imported"))

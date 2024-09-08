import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from statement.models import MerchantCategory


class Command(BaseCommand):
    help = "Populate merchant categories from JSON file"

    def handle_file(self, filename, field):
        with open(filename) as file:
            data = json.load(file)
            for item in data:
                MerchantCategory.objects.update_or_create(
                    code=int(item["mcc"]),
                    defaults={
                        field: item["shortDescription"],
                    },
                )

    def handle(self, *args, **options):
        filename_en = os.path.join(settings.BASE_DIR, "statement/mcc-en.json")
        self.handle_file(filename_en, "description")
        filename_ua = os.path.join(settings.BASE_DIR, "statement/mcc-uk.json")
        self.handle_file(filename_ua, "description_ua")

        self.stdout.write(
            self.style.SUCCESS(
                f"{MerchantCategory.objects.count()} merchant categories populated"
            )
        )

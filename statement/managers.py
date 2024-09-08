from django.db.models import Sum
from django.db.models.query import QuerySet

from currencies.utils import format_amount


class StatementItemQuerySet(QuerySet):
    def total_amounts_by_currency(self):
        qs = (
            self.values("account__currency_code")
            .order_by("account__currency_code")
            .annotate(total_amount=Sum("amount_in_account_currency"))
        )
        return ", ".join(
            [
                format_amount(item["total_amount"], item["account__currency_code"])
                for item in qs
            ]
        )

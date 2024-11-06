import time
from datetime import datetime

from django.utils import timezone

import monobank

from profiles.models import Account
from .models import StatementItem


def import_statement(
    account: Account,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    mono = monobank.Client(account.profile.token)

    from_date = from_date or account.statement_last_updated
    if from_date is None:
        raise ValueError("from_date is required")

    to_date = to_date or timezone.localtime()
    start_date = from_date
    while True:
        finish_date = min(start_date + timezone.timedelta(days=30), to_date)
        print(start_date.strftime("%Y-%m-%d"), finish_date.strftime("%Y-%m-%d"))

        statement_items_data = mono.get_statements(
            account.mono_id, start_date, finish_date
        )

        if "errorDescription" in statement_items_data:
            print(statement_items_data)
            raise Exception(statement_items_data["errorDescription"])

        # TODO: handle >500 operations
        # https://api.monobank.ua/docs/index.html#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get
        for statement_item_data in statement_items_data:
            StatementItem.objects.get_or_create(
                mono_id=statement_item_data["id"],
                account=account,
                defaults={
                    "time": timezone.make_aware(
                        datetime.fromtimestamp(statement_item_data["time"])
                    ),
                    "description": statement_item_data["description"],
                    "merchant_category_id": statement_item_data["mcc"],
                    "hold": statement_item_data["hold"],
                    "amount_in_account_currency": statement_item_data["amount"],
                    "amount_in_operation_currency": statement_item_data[
                        "operationAmount"
                    ],
                    "currency_code": statement_item_data["currencyCode"],
                    "commission_rate": statement_item_data["commissionRate"],
                    "cashback_amount": statement_item_data["cashbackAmount"],
                    "balance": statement_item_data["balance"],
                    "counter_name": statement_item_data.get("counterName", ""),
                    "raw_data": statement_item_data,
                },
            )
        account.statement_last_updated = finish_date
        account.save()

        start_date = finish_date
        if start_date < to_date:
            # Monobank API rate limit
            time.sleep(60)
        else:
            break

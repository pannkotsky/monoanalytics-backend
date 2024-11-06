from django.db import transaction

import monobank

from .models import Account, Jar, Profile


@transaction.atomic
def import_profile(user_id: int, token: str):
    mono = monobank.Client(token)
    client_info = mono.get_client_info()
    raw_data = client_info.copy()
    accounts_data = raw_data.pop("accounts")
    jars_data = raw_data.pop("jars")
    profile, _ = Profile.objects.update_or_create(
        mono_id=raw_data["clientId"],
        user_id=user_id,
        defaults={
            "token": token,
            "name": raw_data["name"],
            "webhook_url": raw_data["webHookUrl"],
            "raw_data": raw_data,
        },
    )
    for account_data in accounts_data:
        cashback_type = account_data.get("cashbackType", "")
        if cashback_type == "None":
            cashback_type = ""
        masked_pans = account_data["maskedPan"]
        Account.objects.update_or_create(
            mono_id=account_data["id"],
            profile=profile,
            defaults={
                "balance": account_data["balance"],
                "credit_limit": account_data["creditLimit"],
                "type": account_data["type"],
                "currency_code": account_data["currencyCode"],
                "cashback_type": cashback_type,
                "masked_pan": masked_pans[0] if masked_pans else "",
                "iban": account_data["iban"],
                "raw_data": account_data,
            },
        )
    for jar_data in jars_data:
        Jar.objects.update_or_create(
            mono_id=jar_data["id"],
            profile=profile,
            defaults={
                "title": jar_data["title"],
                "description": jar_data["description"],
                "currency_code": jar_data["currencyCode"],
                "balance": jar_data["balance"],
                "goal": jar_data["goal"],
                "raw_data": jar_data,
            },
        )

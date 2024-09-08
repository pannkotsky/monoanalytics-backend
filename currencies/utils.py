from django.utils.translation import gettext_lazy as _

# simple dictionary with currencies supported by MonoBank to not put it in the database
CURRENCIES = {
    840: {"symbol": "$", "name": _("US Dollar"), "code": "USD"},
    978: {"symbol": "€", "name": _("Euro"), "code": "EUR"},
    980: {"symbol": "₴", "name": _("Ukrainian Hryvnia"), "code": "UAH"},
}


def get_letter_code(currency_code):
    currency = CURRENCIES.get(currency_code)
    if currency:
        return currency["code"]
    return currency_code


def format_amount(amount, currency_code):
    currency = CURRENCIES.get(currency_code)
    formatted_amount = f"{amount/100:,.2f}"
    if currency:
        return f"{currency['symbol']}{formatted_amount}"
    return f"{currency_code} {formatted_amount}"

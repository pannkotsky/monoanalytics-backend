import pytest

from currencies.utils import format_amount, get_letter_code


@pytest.mark.parametrize(
    "currency_code,expected",
    [
        (840, "USD"),
        (978, "EUR"),
        (980, "UAH"),
        (123, 123),  # Unknown currency code returns as-is
    ],
)
def test_get_letter_code(currency_code, expected):
    assert get_letter_code(currency_code) == expected


@pytest.mark.parametrize(
    "amount,currency_code,expected",
    [
        (1234, 840, "$12.34"),  # USD
        (5000, 978, "€50.00"),  # EUR
        (10000, 980, "₴100.00"),  # UAH
        (2500, 123, "123 25.00"),  # Unknown currency
        (100000, 840, "$1,000.00"),  # Test thousands separator
        (50, 978, "€0.50"),  # Test small amounts
    ],
)
def test_format_amount(amount, currency_code, expected):
    assert format_amount(amount, currency_code) == expected

import pytest

from openapi_schema.util import to_camelcase


@pytest.mark.parametrize(
    "input, expected",
    [
        ("test_field", "testField"),
        ("test_field_with_underscores", "testFieldWithUnderscores"),
        ("test_field_with_numbers_123", "testFieldWithNumbers123"),
        (None, None),
    ],
)
def test_to_camelcase(input, expected):
    assert to_camelcase(input) == expected

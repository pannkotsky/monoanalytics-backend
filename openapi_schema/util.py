import re

from djangorestframework_camel_case.util import camelize_re, underscore_to_camel


def to_camelcase(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(camelize_re, underscore_to_camel, value)
